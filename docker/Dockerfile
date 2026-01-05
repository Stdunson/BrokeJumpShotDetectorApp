FROM python:3.10

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

COPY . .

#Path to model weights
ENV MODEL_WEIGHTS_PATH=/app/MLweights/broke_jump_shot_detector_weights_v5.pth
ENV MAX_VIDEO_MB=25

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
