# DataMate solution, image A (CPU only)

## Approach
Deterministic Python, no machine-learning model.

1. **Read the business folder** (`/data/data/<business_id>/`): every csv, every xlsx sheet, every sqlite table, as text
   cells. The header row is found automatically (title rows such as "Kênh bán: Tất cả" are skipped); sheets or files
   with the same header (monthly sheets, `_1`/`_2026` splits) are concatenated. Money ("24.000đ", "50k", "1tr134"),
   quantities ("2 kg", "1 bao 25kg") and dates (Excel serials, "dd/mm/yyyy", "1 thg 6 2025", ISO) are parsed.
2. **Understand the columns** (`src/dm/schema.py`, `src/dm/canon.py`): the README's "Cột trong `file`" meanings first,
   then a dictionary of Vietnamese POS headers, then ID prefixes in the values (ORD…, PN…, PAY…, SP…, KH…), then token
   rules for unknown headers. Each table gets a role (order lines, orders, payments, products, unit conversions,
   customers, purchases, lots, price history, stock, deliveries, …).
3. **Canonical tables** (`src/dm/assemble.py`): continuation rows of an order take the order's first-row values
   (rulebook §8), subtotal/note rows are dropped, identical rows of one order count once, quantities are converted to
   base units, statuses are mapped to completed / cancelled / returned / delivering.
4. **Question → structured query** (`src/dm/qparse.py`): folding (no diacritics), Telex-typo repair, abbreviations;
   periods (today, last week, this month vs same days of last month, quarters, Tết from `calendar.csv`, …); filters
   (product, category, customer group, payment method, channel, shift, size, staff, …); intent and answer type.
5. **Computation by the rulebook** (`src/dm/engine.py`, `src/dm/engine2.py`): revenue, orders, cancellations, rankings
   with code tie-breaks, shares, price on a day, price-increase effect, purchases, stock at end of day, debts, deliveries.
   Rounding as in the rulebook (money to the đồng, half up; percentages to 2 decimals).
6. **Abstain** whenever the question or the data is not understood. `unanswerable` when the period lies entirely
   outside the shop's data or the shop does not record the information.

An optional rulebook guard (`src/dm/rules.py`, flag `--guard`, **off** in this image) compares the split's rulebook
with the training rulebook (`src/ref/rulebook_train.md`) and abstains on questions that depend on changed rows.

## Models
None. Total parameters: 0. No network access is needed.

## Data
Only the organisers' training split (30 businesses, 3,000 questions with answers) was used, to write the rules and to
check them. No model was trained and no data was generated; see `training_code/README.md`. The public and private test
sets are only read at inference time, by `predict.sh`.

## Run
`bash /code/predict.sh` (no arguments). Input `/data` (read-only), output `/result/submission.jsonl` (written line by
line) and `/result/logs/log.jsonl` (one record per question: `id`, `answer`, `elapsed_ms`, `thinking` = null,
`code` = the function, `inputs`, `output`). Temporary files go to `/tmp/dm_cache`. The run is deterministic: same
input, same output. On a laptop CPU the 1,000 public questions take about 1–3 minutes.

## Layout
- `/code/predict.sh`: entry point
- `/code/src/dm/`: inference code; `/code/src/scripts/eval_dev.py`: scoring against `answers.jsonl`
- `/code/src/ref/rulebook_train.md`: training rulebook (reference for the optional guard)
- `/code/training_code/`: README, pinned requirements, data manifest (no training)
- `/code/models/`: empty (no model)
