#!/bin/bash

# Script to build and run the BrokeShot backend Docker container locally

set -e

echo "Building BrokeShot backend Docker image..."
docker build -f docker/Dockerfile -t broke-detector-backend .

echo "Starting BrokeShot backend container..."
echo "FastAPI server will be available at http://localhost:8000"
echo "API endpoint: http://localhost:8000/analyze"
echo ""
echo "Press Ctrl+C to stop the container"
echo ""

docker run -p 8000:8000 broke-detector-backend
