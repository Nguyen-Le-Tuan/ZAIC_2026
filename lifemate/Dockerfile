FROM python:3.12-slim

ENV HF_HOME=/opt/huggingface \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/lifemate
COPY requirements-lock.txt ./
RUN python -m venv .venv \
    && .venv/bin/pip install --no-cache-dir torch==2.15.0 \
    && .venv/bin/pip install --no-cache-dir -r requirements-lock.txt \
    && .venv/bin/python -c "import torch, transformers; assert torch.__version__.startswith('2.15.0'); assert transformers.__version__ == '5.21.0'"

# The agent loads the model by repo name without a revision argument. Point the
# offline main ref at the exact revision used for the public submission.
RUN HF_HUB_OFFLINE=0 .venv/bin/python -c "from pathlib import Path; from huggingface_hub import snapshot_download; p=Path(snapshot_download(repo_id='Qwen/Qwen3-4B-Instruct-2507', revision='cdbee75f17c0')); assert p.name.startswith('cdbee75f17c0'), p.name; ref=p.parent.parent/'refs'/'main'; ref.parent.mkdir(parents=True, exist_ok=True); ref.write_text(p.name)"

COPY lifemate/ lifemate/
COPY scripts/ scripts/
COPY ckpt/asr_phoft/merged/ ckpt/asr_phoft/merged/
COPY ckpt/q4b4_all/final/ ckpt/q4b4_all/final/

CMD ["bash"]
