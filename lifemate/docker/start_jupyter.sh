#!/usr/bin/env bash
# /code/start_jupyter.sh (organisers' Docker guide 04/11/2026, p. 11-12): JupyterLab on port 9777, password and token
# zac2026, so the organisers can open /code/predict_notebook.ipynb and Run All. They start it with:
#   docker run -it --gpus '"device=0"' -p 9777:9777 -v <data>:/data:ro -v <result>:/result <image> /bin/bash /code/start_jupyter.sh
# The server starts in this script's folder (the notebook shows at the root) and runs on the same Python as
# predict.sh, so the notebook's "Python 3" kernel imports torch, transformers and the lifemate code.
# Testing elsewhere: LIFEMATE_DIR and PY work as in predict.sh.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [ -z "${LIFEMATE_DIR:-}" ]; then
  if [ -f "$HERE/lifemate/infer.py" ]; then LIFEMATE_DIR=$HERE
  elif [ -f "$HERE/../lifemate/infer.py" ]; then LIFEMATE_DIR=$HERE/..
  else LIFEMATE_DIR=/app/lifemate; fi
fi
LIFEMATE_DIR=$(realpath -e "$LIFEMATE_DIR")
if [ -z "${PY:-}" ]; then
  if [ -x "$LIFEMATE_DIR/.venv/bin/python" ]; then PY=$LIFEMATE_DIR/.venv/bin/python; else PY=$(command -v python3); fi
fi
# the kernel inherits these: hash seed fixed before Python starts, models offline, no bytecode next to /data
export LIFEMATE_DIR PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd "$HERE"
ARGS=(--port 9777 --ip 0.0.0.0 --NotebookApp.password='zac2026' --NotebookApp.token='zac2026' --allow-root --no-browser)
if "$PY" -c "import jupyterlab" 2>/dev/null; then
  exec "$PY" -m jupyterlab "${ARGS[@]}"
fi
echo "start_jupyter.sh: jupyterlab is not installed for $PY; trying 'jupyter lab' from PATH (its kernel may lack torch)" >&2
exec jupyter lab "${ARGS[@]}"
