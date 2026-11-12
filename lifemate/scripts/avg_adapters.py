"""Average LoRA adapters trained with the same config and different seeds into ONE adapter, exactly. CPU only.

Each adapter adds dW_i = s * B_i A_i to a base weight (s = lora_alpha/r, or lora_alpha/sqrt(r) with use_rslora).
The output adds the exact mean dW = (dW_1 + ... + dW_N)/N, by rank concatenation:
    A = cat([A_1, ..., A_N], dim=0)            shape [N*r, in]
    B = cat([B_1/N, ..., B_N/N], dim=1)        shape [out, N*r]      so B A = (B_1 A_1 + ... + B_N A_N)/N
r becomes N*r and lora_alpha is set so the scale s is unchanged: N*lora_alpha for plain LoRA (N*a/(N*r) = a/r
exactly), sqrt(N)*lora_alpha with use_rslora. rank_pattern / alpha_pattern values are scaled the same way. No base
model is needed; B/2 is exact in floating point, so for N=2 only the matmuls round.

Cost: N times the LoRA parameters (they count toward the 5B LLM limit: 2 x 60,948,480 = 121,896,960 for the
Qwen3.5-4B A1 adapters) and N times the LoRA FLOPs (same number of kernels). vLLM LoRA serving needs
max_lora_rank >= N*r. Merged into bf16 base weights it costs nothing.

  .venv/bin/python scripts/avg_adapters.py ckpt/X_s0/final ckpt/X_s1/final --out ckpt/X_avg/final
  ... --peft-model-check     also build the base architecture on the meta device (config.json only, no weights),
                             load the result with PeftModel.from_pretrained and check every PEFT LoRA layer

Refuses: configs that differ in anything except inference_mode, lora_dropout, peft_version and the order of
target_modules; DoRA, LoRA biases, modules_to_save, trainable tokens, target_parameters, inits that change the base
weights (PiSSA, LoftQ, ...) and any other config feature it does not know; tensors other than 2-D lora_A/lora_B
weights; key, shape or dtype mismatches.
Verification (default; re-reads the written files): every tensor equals its construction bit for bit; PeftConfig
loads the output and every tensor key/shape matches its target_modules and (pattern-resolved) r; for every module,
s_new * B(A x) vs mean_i s_i * B_i(A_i x) on random x (max abs error, and relative = max abs error / max |ref|),
against an fp32 and an fp64 reference; fails above --tol.
Writes --out through a temporary sibling folder renamed at the end (only when verification passes):
adapter_config.json, adapter_model.safetensors, the other files of the first adapter (tokenizer, chat template),
README.md, avg_meta.json (sources and their sha256, r, alpha, parameter count, verification numbers).
"""
from __future__ import annotations

import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""  # CPU only, set before torch is imported: never touch a GPU in use
os.environ.setdefault("HF_HUB_OFFLINE", "1")  # --peft-model-check reads the base config.json from the local cache

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate import runinfo  # noqa: E402

WEIGHTS, CONFIG, META = "adapter_model.safetensors", "adapter_config.json", "avg_meta.json"
PREFIX = "base_model.model."
A_SUF, B_SUF = ".lora_A.weight", ".lora_B.weight"
NOT_COPIED = {WEIGHTS, "adapter_model.bin", CONFIG, "README.md", META}
# keys that may differ between the sources: they do not change what the saved weights mean at inference
MAY_DIFFER = {"inference_mode", "lora_dropout", "peft_version"}
# keys that may hold any (equal) value; every other key must be unset (None/False/empty) or the script refuses
UNDERSTOOD = {"base_model_name_or_path", "revision", "task_type", "peft_type", "auto_mapping", "inference_mode",
              "r", "lora_alpha", "lora_dropout", "use_rslora", "rank_pattern", "alpha_pattern", "target_modules",
              "exclude_modules", "layers_to_transform", "layers_pattern", "fan_in_fan_out", "init_lora_weights",
              "bias", "peft_version", "megatron_core", "qalora_group_size"}


def refuse(msg: str):
    sys.exit(f"avg_adapters: refused: {msg}")


def read_config(path: Path) -> dict:
    f = path / CONFIG
    if not f.is_file():
        refuse(f"{f} not found")
    return json.loads(f.read_text())


def check_configs(cfgs: list[dict], paths: list[Path]) -> list[str]:
    """Refuse configs that differ in anything that matters or use a feature rank concatenation does not cover."""
    def norm(c):
        c = dict(c)
        for k in ("target_modules", "exclude_modules"):
            if isinstance(c.get(k), list):
                c[k] = sorted(c[k])
        return c

    notes, c0 = [], norm(cfgs[0])
    for c, p in zip(cfgs[1:], paths[1:]):
        c = norm(c)
        diff = sorted(k for k in set(c0) | set(c) if c0.get(k) != c.get(k))
        bad = [k for k in diff if k not in MAY_DIFFER]
        if bad:
            refuse(f"{paths[0]} and {p} differ in " + "; ".join(f"{k}: {c0.get(k)!r} vs {c.get(k)!r}" for k in bad))
        notes += [f"{k} differs ({c0.get(k)!r} in {paths[0]}, {c.get(k)!r} in {p}); it does not change the weights"
                  for k in diff]
    c, problems = cfgs[0], []
    if c.get("peft_type") != "LORA":
        problems.append(f"peft_type={c.get('peft_type')!r}")
    if not isinstance(c.get("r"), int) or c["r"] <= 0:
        problems.append(f"r={c.get('r')!r}")
    if c.get("bias", "none") != "none":
        problems.append(f"bias={c['bias']!r}")
    if c.get("init_lora_weights", True) not in (True, False, "gaussian"):
        problems.append(f"init_lora_weights={c['init_lora_weights']!r} (changes the base weights)")
    problems += [f"{k}={v!r}" for k, v in c.items() if k not in UNDERSTOOD and v]
    if problems:
        refuse("unsupported LoRA features: " + ", ".join(problems) + " (rank concatenation is exact only for plain "
               "LoRA A/B weights; a mean of DoRA magnitudes, biases or saved modules is not handled here)")
    return notes


def r_alpha(cfg: dict, module: str) -> tuple:
    """r and lora_alpha of one module exactly as PEFT resolves them (rank_pattern / alpha_pattern)."""
    from peft.utils.other import get_pattern_key

    name = module[len(PREFIX):]
    rp, ap = cfg.get("rank_pattern") or {}, cfg.get("alpha_pattern") or {}
    return (rp.get(get_pattern_key(rp.keys(), name), cfg["r"]),
            ap.get(get_pattern_key(ap.keys(), name), cfg["lora_alpha"]))


def scale_of(cfg: dict, r, alpha) -> float:
    return alpha / math.sqrt(r) if cfg.get("use_rslora") else alpha / r


def lora_modules(keys, where) -> list[str]:
    mods: dict[str, set] = {}
    for k in keys:
        if not k.startswith(PREFIX) or not k.endswith((A_SUF, B_SUF)):
            refuse(f"{where}: tensor {k} is not a lora_A/lora_B weight (only plain LoRA layers are supported)")
        mods.setdefault(k[:-len(A_SUF)], set()).add(k)
    broken = [m for m, ks in mods.items() if len(ks) != 2]
    if broken:
        refuse(f"{where}: {len(broken)} modules lack lora_A or lora_B, e.g. {broken[0]}")
    return sorted(mods)


def averaged_config(cfg: dict, n: int) -> dict:
    rs = cfg.get("use_rslora")

    def alpha(a):
        return a * math.sqrt(n) if rs else a * n

    c = json.loads(json.dumps(cfg))
    c["r"] = cfg["r"] * n
    c["lora_alpha"] = alpha(cfg["lora_alpha"])
    c["rank_pattern"] = {p: v * n for p, v in (cfg.get("rank_pattern") or {}).items()}
    c["alpha_pattern"] = {p: alpha(v) for p, v in (cfg.get("alpha_pattern") or {}).items()}
    c["inference_mode"] = True
    return c


def build(srcs: list[Path], cfgs: list[dict]):
    """The averaged state dict (A concatenated, B/N concatenated) after every key/shape/dtype check."""
    import torch
    from safetensors.torch import load_file

    for p in srcs:
        if not (p / WEIGHTS).is_file():
            refuse(f"{p / WEIGHTS} not found (only safetensors adapters are supported)")
    sds = [load_file(str(p / WEIGHTS)) for p in srcs]
    modules = lora_modules(sds[0].keys(), srcs[0])
    for sd, p in zip(sds[1:], srcs[1:]):
        if set(sd) != set(sds[0]):
            refuse(f"{srcs[0]} and {p} hold different tensors: {sorted(set(sd) ^ set(sds[0]))[:4]} ...")
    n = len(sds)
    out = {}
    for m in modules:
        a, b = [sd[m + A_SUF] for sd in sds], [sd[m + B_SUF] for sd in sds]
        sig = {(tuple(x.shape), tuple(y.shape), x.dtype, y.dtype) for x, y in zip(a, b)}
        if len(sig) != 1:
            refuse(f"{m}: shapes/dtypes differ between the adapters: {sorted(map(str, sig))}")
        r, _ = r_alpha(cfgs[0], m)
        if a[0].dim() != 2 or b[0].dim() != 2 or a[0].shape[0] != r or b[0].shape[1] != r:
            refuse(f"{m}: lora_A {tuple(a[0].shape)} / lora_B {tuple(b[0].shape)} do not fit r={r} of the config")
        out[m + A_SUF] = torch.cat(a, 0).contiguous()
        out[m + B_SUF] = torch.cat([(x.double() / n).to(x.dtype) for x in b], 1).contiguous()  # exact for n=2
    return out, modules, [sum(t.numel() for t in sd.values()) for sd in sds]


def verify(out_dir: Path, srcs: list[Path], probes: int, seed: int) -> dict:
    """Re-read the written adapter; compare it with the sources tensor by tensor and on random inputs."""
    import torch
    from peft import PeftConfig
    from peft.tuners.tuners_utils import check_target_module_exists
    from safetensors import safe_open

    pc = PeftConfig.from_pretrained(str(out_dir))
    if type(pc).__name__ != "LoraConfig":
        raise AssertionError(f"PeftConfig.from_pretrained gave {type(pc).__name__}, not LoraConfig")
    new = {"r": pc.r, "lora_alpha": pc.lora_alpha, "use_rslora": pc.use_rslora,
           "rank_pattern": pc.rank_pattern, "alpha_pattern": pc.alpha_pattern}
    cfgs = [read_config(p) for p in srcs]
    n, g = len(srcs), torch.Generator().manual_seed(seed)
    fo = safe_open(str(out_dir / WEIGHTS), "pt")
    fs = [safe_open(str(p / WEIGHTS), "pt") for p in srcs]
    modules = lora_modules(fo.keys(), out_dir)
    if set(fo.keys()) != set(fs[0].keys()):
        raise AssertionError("the output holds other tensor keys than the sources")
    res = {"n_modules": len(modules), "probes": probes, "seed": seed, "tensors_exact": True,
           "max_abs_err_fp32": 0.0, "max_rel_err_fp32": 0.0, "max_abs_err_vs_fp64": 0.0, "max_rel_err_vs_fp64": 0.0,
           "min_rel_diff_one_seed_vs_mean": math.inf, "scales": set(), "ranks": set()}
    for m in modules:
        if not check_target_module_exists(pc, m[len(PREFIX):]):
            raise AssertionError(f"{m} does not match target_modules {pc.target_modules}")
        A, B = fo.get_tensor(m + A_SUF), fo.get_tensor(m + B_SUF)
        r, alpha = r_alpha(new, m)
        if tuple(A.shape)[0] != r or tuple(B.shape)[1] != r:
            raise AssertionError(f"{m}: shapes {tuple(A.shape)} {tuple(B.shape)} vs r={r} in the PEFT config")
        As, Bs = [f.get_tensor(m + A_SUF) for f in fs], [f.get_tensor(m + B_SUF) for f in fs]
        B_built = torch.cat([(x.double() / n).to(x.dtype) for x in Bs], 1)
        res["tensors_exact"] &= torch.equal(A, torch.cat(As, 0)) and torch.equal(B, B_built)
        s = scale_of(new, r, alpha)
        ss = [scale_of(c, *r_alpha(c, m)) for c in cfgs]
        res["scales"].add(s)
        res["ranks"].add(r)
        x = torch.randn(probes, A.shape[1], generator=g)
        y = s * ((x @ A.float().T) @ B.float().T)  # what the averaged adapter adds, in fp32
        ys = [si * ((x @ a.float().T) @ b.float().T) for si, a, b in zip(ss, As, Bs)]
        ref32 = torch.stack(ys).mean(0)
        ys64 = [si * ((x.double() @ a.double().T) @ b.double().T) for si, a, b in zip(ss, As, Bs)]
        ref64 = torch.stack(ys64).mean(0)
        top32, top64 = ref32.abs().max().item(), ref64.abs().max().item()
        e32 = (y - ref32).abs().max().item()
        e64 = (y.double() - ref64).abs().max().item()
        rel32, rel64 = (e32 / top32 if top32 else e32), (e64 / top64 if top64 else e64)
        sens = (ys64[0] - ref64).abs().max().item() / top64 if top64 else 0.0
        if rel32 > res["max_rel_err_fp32"]:
            res["worst_module"] = m
        res["max_abs_err_fp32"] = max(res["max_abs_err_fp32"], e32)
        res["max_rel_err_fp32"] = max(res["max_rel_err_fp32"], rel32)
        res["max_abs_err_vs_fp64"] = max(res["max_abs_err_vs_fp64"], e64)
        res["max_rel_err_vs_fp64"] = max(res["max_rel_err_vs_fp64"], rel64)
        res["min_rel_diff_one_seed_vs_mean"] = min(res["min_rel_diff_one_seed_vs_mean"], sens)
    res["scales"], res["ranks"] = sorted(res["scales"]), sorted(res["ranks"])
    return res


def peft_model_check(out_dir: Path, srcs: list[Path], base: str, probes: int, seed: int) -> dict:
    """PeftModel.from_pretrained on the base architecture built on the meta device (config only): every PEFT LoRA
    layer must get its tensors from the file, the expected r and scaling, and its forward must output the mean of
    the sources. The targeted base Linear layers get an all-zero CPU weight of stride 0 (4 bytes each): PEFT moves
    loaded LoRA tensors to the device of the base weight, and the layer forward then returns exactly the LoRA part."""
    import torch
    from peft import PeftConfig, PeftModel
    from peft.tuners.lora import LoraLayer
    from peft.tuners.tuners_utils import check_target_module_exists
    from safetensors import safe_open
    from transformers import AutoConfig, AutoModelForCausalLM

    with torch.device("meta"):
        model = AutoModelForCausalLM.from_config(AutoConfig.from_pretrained(base))
    pc = PeftConfig.from_pretrained(str(out_dir))
    for name, mod in model.named_modules():
        if isinstance(mod, torch.nn.Linear) and check_target_module_exists(pc, name):
            mod.weight = torch.nn.Parameter(torch.zeros((), dtype=torch.float32).expand(mod.out_features,
                                                                                        mod.in_features),
                                            requires_grad=False)
            if mod.bias is not None:
                mod.bias = torch.nn.Parameter(torch.zeros(mod.out_features), requires_grad=False)
    pm = PeftModel.from_pretrained(model, str(out_dir), low_cpu_mem_usage=True)
    pm.eval()
    layers = {k: v for k, v in pm.named_modules() if isinstance(v, LoraLayer)}
    fo = safe_open(str(out_dir / WEIGHTS), "pt")
    fs = [safe_open(str(p / WEIGHTS), "pt") for p in srcs]
    cfgs = [read_config(p) for p in srcs]
    modules = lora_modules(fo.keys(), out_dir)
    res = {"base": base, "peft_lora_layers": len(layers), "file_modules": len(modules),
           "not_in_model": [m for m in modules if m not in layers][:5],
           "without_weights": [k for k in layers if k not in set(modules)][:5],
           "r": sorted({v.r["default"] for v in layers.values()}),
           "scaling": sorted({v.scaling["default"] for v in layers.values()}), "max_rel_err_vs_fp64": 0.0,
           "weights_equal_file": True}
    g = torch.Generator().manual_seed(seed)
    for m in modules:
        if m not in layers:
            continue
        lay = layers[m]
        A, B = lay.lora_A["default"].weight, lay.lora_B["default"].weight
        if A.is_meta or B.is_meta:
            res["weights_equal_file"] = False
            continue
        same = [torch.equal(w, fo.get_tensor(m + suf).to(w.dtype)) for w, suf in ((A, A_SUF), (B, B_SUF))]
        res["weights_equal_file"] &= all(same)  # PEFT holds them in fp32 here; .to() only upcasts, so still exact
        x = torch.randn(probes, A.shape[1], generator=g)
        with torch.no_grad():
            y = lay(x)  # PEFT's own LoRA forward (dropout off in eval); the zero base weight adds exactly 0
        ref =torch.stack([scale_of(c, *r_alpha(c, m)) * ((x.double() @ f.get_tensor(m + A_SUF).double().T)
                                                          @ f.get_tensor(m + B_SUF).double().T)
                           for c, f in zip(cfgs, fs)]).mean(0)
        top = ref.abs().max().item()
        rel = (y.double() - ref).abs().max().item() / (top or 1.0)
        res["max_rel_err_vs_fp64"] = max(res["max_rel_err_vs_fp64"], rel)
    res["ok"] = (not res["not_in_model"] and not res["without_weights"] and res["weights_equal_file"]
                 and len(layers) == len(modules))
    return res


def readme(meta: dict) -> str:
    src = "\n".join(f"- `{s['path']}`: r={s['r']}, lora_alpha={s['lora_alpha']}, {s['n_params']:,} params, "
                    f"adapter_model.safetensors sha256 `{s['weights_sha256']}`" for s in meta["sources"])
    v = meta.get("verify") or {}
    ver = ("not run (--no-verify)" if not v else
           f"{v['n_modules']} modules, {v['probes']} random inputs each: max abs error {v['max_abs_err_fp32']:.3g}, "
           f"max relative error {v['max_rel_err_fp32']:.3g} (fp32 vs fp32 mean); vs an fp64 mean "
           f"{v['max_rel_err_vs_fp64']:.3g}; tensors equal their construction bit for bit: {v['tensors_exact']}")
    pmc = meta.get("peft_model_check")
    pmc = (f"\n- PeftModel.from_pretrained on the meta-device base `{pmc['base']}`: {pmc['peft_lora_layers']} LoRA "
           f"layers, r {pmc['r']}, scaling {pmc['scaling']}, max relative error {pmc['max_rel_err_vs_fp64']:.3g}, "
           f"ok={pmc['ok']}" if pmc else "")
    o = meta["output"]
    return f"""# Seed-averaged LoRA adapter

Written by `lifemate/scripts/avg_adapters.py` on {meta['created']}. Base model: `{meta['base_model']}`.
Load it like any PEFT adapter (`PeftModel.from_pretrained(base, this_dir)`).

The weight update is exactly the mean of the {len(meta['sources'])} source adapters,
dW = (dW_1 + ... + dW_N) / N, built by rank concatenation: lora_A = cat(A_i, dim 0), lora_B = cat(B_i / N, dim 1).
r = {o['r']} (N x {meta['sources'][0]['r']}), lora_alpha = {o['lora_alpha']}, so the LoRA scale stays {o['scale']}.
It has {o['n_params']:,} LoRA parameters (the sum of the sources); they count toward the LLM size limit.
LoRA compute per token is N times the sources' (same number of kernels); vLLM needs max_lora_rank >= {o['r']}.

Sources:
{src}

Verification:
- {ver}{pmc}

Details (hashes, versions, all numbers): `avg_meta.json`.
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("adapters", nargs="+", help="PEFT LoRA adapter folders (same config, different seeds), at least 2")
    ap.add_argument("--out", required=True, help="output adapter folder (must not exist)")
    ap.add_argument("--overwrite", action="store_true", help="replace --out if it is an earlier output of this script")
    ap.add_argument("--probes", type=int, default=8, help="random inputs per module in the verification")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tol", type=float, default=1e-5, help="largest relative error (fp32) the verification accepts")
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--peft-model-check", action="store_true",
                    help="also load the output with PeftModel.from_pretrained on the meta-device base architecture")
    ap.add_argument("--base", help="model id/folder for --peft-model-check (default: base_model_name_or_path)")
    a = ap.parse_args()
    if len(a.adapters) < 2:
        ap.error("give at least two adapters")
    srcs = [Path(p) for p in a.adapters]
    if len({p.resolve() for p in srcs}) < len(srcs):
        refuse("the same adapter is given more than once")
    out = Path(a.out)
    if out.exists() and a.overwrite and not (out / META).is_file():
        refuse(f"--overwrite only replaces an earlier output of this script; {out} has no {META}")
    runinfo.refuse_existing(out, overwrite=a.overwrite)

    cfgs = [read_config(p) for p in srcs]
    notes = check_configs(cfgs, srcs)
    for s in notes:
        print("note:", s)
    sd, modules, src_params = build(srcs, cfgs)
    cfg = averaged_config(cfgs[0], len(srcs))

    import torch
    from safetensors.torch import save_file

    tmp = out.parent / f".{out.name}.tmp-{os.getpid()}"
    tmp.mkdir(parents=True)
    try:
        (tmp / CONFIG).write_text(json.dumps(cfg, indent=2) + "\n")
        save_file(sd, str(tmp / WEIGHTS), metadata={"format": "pt"})
        n_params = sum(t.numel() for t in sd.values())
        dtypes = sorted({str(t.dtype).replace("torch.", "") for t in sd.values()})
        del sd
        copied = {}
        for f in sorted(srcs[0].iterdir()):
            if f.is_file() and f.name not in NOT_COPIED:
                shutil.copy2(f, tmp / f.name)
                h = runinfo.sha256_file(f)
                same = [(p / f.name).is_file() and runinfo.sha256_file(p / f.name) == h for p in srcs[1:]]
                copied[f.name] = {"sha256": h, "identical_in_all_sources": all(same)}
                if not all(same):
                    print(f"note: {f.name} differs between the sources; copied from {srcs[0]}")
        print(f"averaged {len(srcs)} adapters: {len(modules)} LoRA modules, r {cfgs[0]['r']} -> {cfg['r']}, "
              f"lora_alpha {cfgs[0]['lora_alpha']} -> {cfg['lora_alpha']}, "
              f"scale {scale_of(cfgs[0], cfgs[0]['r'], cfgs[0]['lora_alpha'])} -> "
              f"{scale_of(cfg, cfg['r'], cfg['lora_alpha'])}")
        print(f"parameters: {' + '.join(f'{p:,}' for p in src_params)} = {n_params:,} in the averaged adapter")
        if n_params != sum(src_params):
            raise AssertionError("parameter count of the output is not the sum of the sources")

        ver = pmc = None
        if not a.no_verify:
            ver = verify(tmp, srcs, a.probes, a.seed)
            print("verify:", json.dumps(ver))
            if not ver["tensors_exact"] or not ver["max_rel_err_fp32"] <= a.tol:
                raise AssertionError(f"verification failed (tol {a.tol})")
        if a.peft_model_check:
            pmc = peft_model_check(tmp, srcs, a.base or cfg["base_model_name_or_path"], min(a.probes, 4), a.seed + 1)
            print("peft_model_check:", json.dumps(pmc))
            if not pmc["ok"] or not pmc["max_rel_err_vs_fp64"] <= a.tol:
                raise AssertionError("PeftModel load check failed")

        meta = {
            "created": runinfo.now(), "argv": sys.argv, "base_model": cfg["base_model_name_or_path"],
            "method": "rank concatenation: lora_A = cat(A_i, dim=0), lora_B = cat(B_i/N, dim=1); r and lora_alpha "
                      "scaled so the LoRA scale is unchanged; dW = mean_i dW_i exactly",
            "sources": [{"path": str(p), "resolved": str(p.resolve()), "r": c["r"], "lora_alpha": c["lora_alpha"],
                         "scale": scale_of(c, c["r"], c["lora_alpha"]), "n_params": k,
                         "weights_sha256": runinfo.sha256_file(p / WEIGHTS),
                         "config_sha256": runinfo.sha256_file(p / CONFIG), "dir_sha256": runinfo.sha256_dir(p)}
                        for p, c, k in zip(srcs, cfgs, src_params)],
            "output": {"r": cfg["r"], "lora_alpha": cfg["lora_alpha"], "use_rslora": bool(cfg.get("use_rslora")),
                       "rank_pattern": cfg["rank_pattern"], "alpha_pattern": cfg["alpha_pattern"],
                       "scale": scale_of(cfg, cfg["r"], cfg["lora_alpha"]), "n_params": n_params,
                       "n_modules": len(modules), "dtypes": dtypes,
                       "weights_sha256": runinfo.sha256_file(tmp / WEIGHTS)},
            "copied_from_first_source": copied, "config_notes": notes, "verify": ver, "peft_model_check": pmc,
            "git": runinfo.git_state(), "env": runinfo.env_info(),
        }
        (tmp / "README.md").write_text(readme(meta))
        runinfo.write_json(tmp / META, meta)
        if out.exists():
            shutil.rmtree(out)  # only an earlier output of this script (checked above)
        tmp.rename(out)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    print(f"wrote {out} ({n_params:,} LoRA parameters, torch {torch.__version__})")


if __name__ == "__main__":
    main()
