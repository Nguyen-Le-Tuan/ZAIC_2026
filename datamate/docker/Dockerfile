# DataMate, image A: deterministic rules on CPU, no model weights. Build context: the datamate/ folder.
FROM python:3.12.14-slim
ENTRYPOINT []
ENV PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 TZ=Asia/Ho_Chi_Minh
WORKDIR /code
COPY docker/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt
COPY docker/training_code/ /code/training_code/
COPY dm/ /code/src/dm/
COPY scripts/ /code/src/scripts/
COPY ref/ /code/src/ref/
COPY docker/README.md /code/README.md
COPY docker/predict.sh /code/predict.sh
RUN chmod +x /code/predict.sh && mkdir -p /code/models && python -c "import sys; sys.path.insert(0, '/code/src'); import dm.run"
CMD ["bash", "/code/predict.sh"]
