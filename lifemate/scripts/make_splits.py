"""Dev splits of train (written to splits/):

  dev_random.txt / fit_random.txt   15% of train, stratified by category (execute / ask_missing / out_of_scope)
  dev_lao.txt / fit_lao.txt         leave-apps-out: dev = every sample whose gold calls or history calls use a held-out app.
                                    Training on fit_lao must also drop the held-out apps from installed_apps,
                                    so their schemas are never seen (mimics the unseen apps of public/private test).
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifemate.data import load_split  # noqa: E402
from lifemate.scorer import category  # noqa: E402
from lifemate.sft import used_apps as apps_of_calls  # noqa: E402  (also counts sys.ask_missing_info's tool_name)

# train-only apps (absent from public_test), mixed kinds: lookup+write, devices, finance-like
HELDOUT_APPS = ["library", "robot_vacuum", "loyalty", "medication", "video_meeting", "home_security"]


def used_apps(s):
    calls = list(s["label"]["tool_calls"])
    for h in s["history"]:
        calls += h.get("tool_calls") or []
    return apps_of_calls(calls)


def main():
    out = Path(__file__).resolve().parents[1] / "splits"
    out.mkdir(exist_ok=True)
    train = load_split("train")

    rng = random.Random(0)
    by_cat = defaultdict(list)
    for s in train:
        by_cat[category(s["label"]["tool_calls"])].append(s["id"])
    dev = set()
    for ids in by_cat.values():
        dev |= set(rng.sample(ids, round(0.15 * len(ids))))
    (out / "dev_random.txt").write_text("\n".join(sorted(dev)) + "\n")
    (out / "fit_random.txt").write_text("\n".join(sorted(s["id"] for s in train if s["id"] not in dev)) + "\n")

    held = set(HELDOUT_APPS)
    lao = {s["id"] for s in train if used_apps(s) & held}
    (out / "dev_lao.txt").write_text("\n".join(sorted(lao)) + "\n")
    (out / "fit_lao.txt").write_text("\n".join(sorted(s["id"] for s in train if s["id"] not in lao)) + "\n")
    (out / "heldout_apps.json").write_text(json.dumps(HELDOUT_APPS) + "\n")

    cats = lambda ids: dict(sorted({c: sum(1 for s in train if s["id"] in ids and category(s["label"]["tool_calls"]) == c) for c in by_cat}.items()))  # noqa: E731
    print("dev_random", len(dev), cats(dev))
    print("dev_lao", len(lao), cats(lao), "held-out apps:", HELDOUT_APPS)


if __name__ == "__main__":
    main()
