#!/bin/bash

# Script to build and run the BrokeShot backend Docker container locally

set -e

echo "Building BrokeShot backend Docker image..."

#Old: docker build -f docker/Dockerfile -t broke-detector-backend .
docker build \
  -f docker/Dockerfile \
  --build-arg MODEL_URL="https://huggingface.co/Stdunson/BrokeJumpshotDetectorWeights" \
  -t broke-jumpshot-backend .


echo "Starting BrokeShot backend container..."
echo "FastAPI server will be available at http://localhost:8000"
echo "API endpoint: http://localhost:8000/analyze"
echo ""
echo "Press Ctrl+C to stop the container"
echo ""

docker run --env-file .env -e MODEL_WEIGHTS_PATH=/app/MLweights/broke_jump_shot_detector_weights_v4.pth -p 8000:8000 broke-detector-backend
