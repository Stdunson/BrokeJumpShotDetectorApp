FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

#Install dependencies
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

ARG MODEL_URL
ENV MODEL_WEIGHTS_PATH=/app/MLweights/broke_jump_shot_detector_weights_v5.pth

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/MLweights \
  && curl -L "$MODEL_URL" -o "$MODEL_WEIGHTS_PATH" \
  && ls -lh /app/MLweights

COPY . .

#Path to model weights
ENV MAX_VIDEO_MB=25

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
