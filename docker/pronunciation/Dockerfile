FROM python:3.12-slim

ENV HF_HOME=/models/huggingface \
    OPENPRONOUNCE_CACHE_DIR=/models/openpronounce \
    OPENPRONOUNCE_TTS=piper \
    OPENPRONOUNCE_TTS_VOICE=en_US-lessac-medium \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg espeak-ng libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir "openpronounce[tts-piper]==0.3.0" \
       "fastapi==0.115.12" "uvicorn[standard]==0.34.2" "python-multipart==0.0.20"

WORKDIR /app
COPY docker/pronunciation/server.py /app/server.py
RUN useradd --create-home --uid 10001 scorer \
    && mkdir -p /models/huggingface /models/openpronounce \
    && chown -R scorer:scorer /app /models

USER scorer
EXPOSE 9000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:9000/health || exit 1
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9000", "--workers", "1"]
