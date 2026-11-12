# Training code

**No training and no data generation were performed.** The solution is a set of hand-written rules (Python) for
reading the files, understanding the questions and computing the answers.

How the rules were developed and checked, on the organisers' training split only:

- Split (fixed before writing rules): a lockbox of 621 questions (`int(sha256(id), 16) % 5 == 0`) and 5 held-out
  businesses (`biz_109`, `biz_110`, `biz_116`, `biz_121`, `biz_124`) were set aside; rules were written by reading the
  remaining 1,990 questions and the files of the other 25 businesses.
- Verification (training split mounted at `<train>`):

      cd /code/src
      python -m dm.run --split <train> --out /tmp/train_run --cache /tmp/dm_cache
      python scripts/eval_dev.py <train> /tmp/train_run <ids.txt>     # ids.txt: question ids to score

- Result of the submitted code on the 3,000 training questions: PA 0.911 (2,807 correct, 73 wrong, 120 abstain).

Pinned dependencies: `requirements.txt` (same as inference). Python 3.12. Nothing is random; no seed is needed.
