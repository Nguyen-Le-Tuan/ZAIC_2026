"""Score generated D1 labels against the real train labels of the same apps (CPU, labels only).

  cd lifemate && PYTHONPATH=. python3 scripts/d1_compare.py --tag lao0 [--apps library,loyalty]

For every tool of the apps in gen/d1_<tag>_scen.jsonl:
  keys     share of calls per argument-key set, generated vs real; overlap = sum of min(share) (1 = same mix)
  reads    for write tools: share of calls preceded by a read of the same app (and of contacts), generated vs real
  values   a few examples of real argument values next to generated ones
and for the samples that use each app: execute / lookup / ask shares and calls per sample.
The generated side knows nothing of these labels when the generator was written blind (see the commit message of
lifemate/d1_gen.py); numbers from this script must not be used to tune a generator whose data is then scored on dev.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from lifemate.data import catalog_tools, load_catalog, load_jsonl, load_split

C = collections.Counter
ASK = "sys.ask_missing_info"


def profile(samples: list[list[dict]], apps: set[str], tools: dict):
    keys, pre, vals, kinds, ncalls = collections.defaultdict(C), collections.defaultdict(C), collections.defaultdict(list), collections.defaultdict(C), collections.defaultdict(list)
    for calls in samples:
        used = {c["name"].split(".")[0] for c in calls} & apps
        asked = {c["arguments"].get("tool_name", "").split(".")[0] for c in calls if c["name"] == ASK} & apps
        for a in used | asked:
            mine = [c for c in calls if c["name"].split(".")[0] == a]
            k = "ask" if a in asked else ("lookup" if all(tools[c["name"]]["kind"] == "read" for c in mine) else "execute")
            kinds[a][k] += 1
            ncalls[a].append(len(mine))
        for i, c in enumerate(calls):
            app = c["name"].split(".")[0]
            if app not in apps:
                continue
            keys[c["name"]][json.dumps(sorted(c["arguments"]), ensure_ascii=False)] += 1
            if len(vals[c["name"]]) < 400:
                vals[c["name"]].append(c["arguments"])
            if tools[c["name"]]["kind"] == "write":
                before = {x["name"] for x in calls[:i] if tools.get(x["name"], {}).get("kind") == "read"}
                same = sorted(n for n in before if n.split(".")[0] == app)
                pre[c["name"]]["+".join(same) or "(none)"] += 1
                pre[c["name"] + " | contacts.search"]["yes" if "contacts.search" in before else "no"] += 1
    return keys, pre, vals, kinds, ncalls


def share(c: C) -> dict:
    n = sum(c.values())
    return {k: v / n for k, v in c.items()}


def overlap(a: C, b: C) -> float:
    sa, sb = share(a), share(b)
    return sum(min(sa.get(k, 0), sb.get(k, 0)) for k in set(sa) | set(sb))


def fmt(c: C) -> str:
    n = sum(c.values())
    return ", ".join(f"{k} {100 * v / n:.0f}%" for k, v in c.most_common(4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--apps")
    ap.add_argument("--json")
    ap.add_argument("--asks", action="store_true", help="also compare the clarification programmes")
    ap.add_argument("--ids", help="file of train ids the real side is restricted to (e.g. splits/fit_random.txt)")
    a = ap.parse_args()
    gen = load_jsonl(Path("gen") / f"d1_{a.tag}_scen.jsonl")
    apps = set(a.apps.split(",")) if a.apps else {g["app"] for g in gen}
    tools = catalog_tools(load_catalog("train"))
    keep = set(Path(a.ids).read_text().split()) if a.ids else None
    real = [s["label"]["tool_calls"] for s in load_split("train") if keep is None or s["id"] in keep]
    G = profile([g["calls"] for g in gen], apps, tools)
    R = profile(real, apps, tools)
    out, wsum, wtot = {}, 0.0, 0
    for app in sorted(apps):
        print(f"\n=== {app}: samples real {sum(R[3][app].values())} / generated {sum(G[3][app].values())}")
        print(f"  kinds    real: {fmt(R[3][app])} | generated: {fmt(G[3][app])}")
        if R[4][app] and G[4][app]:
            print(f"  calls of this app per sample: real {sum(R[4][app]) / len(R[4][app]):.2f} | generated {sum(G[4][app]) / len(G[4][app]):.2f}")
        for name in sorted(n for n in tools if n.startswith(app + ".")):
            rk, gk = R[0].get(name, C()), G[0].get(name, C())
            nr, ng = sum(rk.values()), sum(gk.values())
            if not nr and not ng:
                continue
            ov = overlap(rk, gk) if nr and ng else 0.0
            if nr:
                wsum += ov * nr
                wtot += nr
            print(f"  {name}  real n={nr}, generated n={ng}, key-set overlap {ov:.2f}")
            print(f"      keys  real: {fmt(rk) or '-'}\n            gen : {fmt(gk) or '-'}")
            if tools[name]["kind"] == "write":
                print(f"      read before (same app)  real: {fmt(R[1].get(name, C())) or '-'} | gen: {fmt(G[1].get(name, C())) or '-'}")
                rc, gc = R[1].get(name + " | contacts.search", C()), G[1].get(name + " | contacts.search", C())
                if rc.get("yes") or gc.get("yes"):
                    print(f"      contacts.search before  real: {fmt(rc)} | gen: {fmt(gc)}")
            ex_r = [json.dumps(v, ensure_ascii=False) for v in R[2].get(name, [])[:3]]
            ex_g = [json.dumps(v, ensure_ascii=False) for v in G[2].get(name, [])[:2]]
            print(f"      e.g.  real: {' ; '.join(ex_r)[:330]}\n            gen : {' ; '.join(ex_g)[:230]}")
            out[name] = {"real_n": nr, "gen_n": ng, "overlap": round(ov, 3)}
    if a.asks:   # clarifications: which tool and parameters are asked, and which reads come before
        def asks(samples):
            what, pre, side = C(), C(), C()
            for calls in samples:
                q = next((c for c in calls if c["name"] == ASK), None)
                if q is None:
                    continue
                key = f"{q['arguments'].get('tool_name')} {q['arguments'].get('params')}"
                what[key] += 1
                reads = [c["name"] for c in calls if c["name"] != ASK and tools[c["name"]]["kind"] == "read" and c["name"].split(".")[0] in ("contacts", q["arguments"].get("tool_name", "").split(".")[0])]
                pre[key + " <- " + ("+".join(reads) or "(no look-up)")] += 1
                side["with another request" if any(tools.get(c["name"], {}).get("kind") == "write" for c in calls) else "alone"] += 1
            return what, pre, side
        gw, gp, gs = asks([g["calls"] for g in gen])
        rw, rp, rs = asks(real)
        rw_in = C({k: v for k, v in rw.items() if k in gw})
        print(f"\n=== clarifications: real {sum(rw.values())} (of which the generated programmes cover {sum(rw_in.values())} = {100 * sum(rw_in.values()) / max(sum(rw.values()), 1):.0f}%), generated {sum(gw.values())}")
        print(f"  mix of (tool, params) within the covered ones, overlap {overlap(rw_in, gw):.2f}")
        for k, v in rw_in.most_common():
            print(f"    {k:55s} real {100 * v / sum(rw_in.values()):4.0f}% | gen {100 * gw[k] / sum(gw.values()):4.0f}%")
        rp_in = C({k: v for k, v in rp.items() if k.split(" <- ")[0] in gw})
        print(f"  look-up before the question, overlap {overlap(rp_in, gp):.2f}")
        for k, v in rp_in.most_common(12):
            print(f"    {k:95s} real {v:3d} | gen {gp.get(k, 0):3d}")
        print(f"  alone / with another request: real {fmt(rs)} | gen {fmt(gs)}")
        print("  real clarifications not covered (top):", [(k, v) for k, v in rw.most_common(40) if k not in gw][:10])
    print(f"\nkey-set overlap, weighted by how often the real labels call each tool: {wsum / max(wtot, 1):.3f} over {wtot} real calls")
    never = sorted(n for n, v in out.items() if v["real_n"] and not v["gen_n"])
    print("real tools the generator never calls:", never)
    if a.json:
        Path(a.json).write_text(json.dumps({"tools": out, "weighted_overlap": wsum / max(wtot, 1), "never_generated": never}, indent=1) + "\n")


if __name__ == "__main__":
    main()
