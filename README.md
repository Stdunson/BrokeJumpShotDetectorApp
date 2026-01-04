# BrokeJumpShotDetectorApp

Welcome to the broke jumpshot detector by Shavaughn Dunson. This project was started on November 1st, 2025 and is currently ongoing. More information about processes and usage directions will be updated as the project develops.

## Frontend
SwiftUI frontend, swiftdata for persistence

## Backend
FastAPI backend, incorporates many scripts, including all scripts in backend, video_processor, and pose_classifier, as well as a model from MLmodels directory

### Request
POST \analyze

### Response: JSON
```json
{
  "score": 7,
  "is_broke": true,
  "max_score": 9,
  "phases": {
    "shot_pocket": {
      "prediction": 1,
      "confidence": 0.92,
      "phase": "shot pocket"
    },
    "set_point": {
      "prediction": 0,
      "confidence": 0.78,
      "phase": "set point"
    },
    "follow_through": {
      "prediction": 1,
      "confidence": 0.85,
      "phase": "follow through"
    }
  },
  "message": "Shot is BROKE. Score: 7/9. Improve the phases marked as broken.",
  "timestamp": "2025-12-20T10:30:00.123456"
}
```

## ML
MLP with mediapipe keypoins, phase as inputs, trained using PyTorch

## Usage Directions

### Running the Backend

#### Option 1: Docker (Recommended for Local Testing)
1. Navigate to the project root directory
2. Run the backend script:
   ```bash
   chmod +x docker/run-backend.sh
   ./docker/run-backend.sh
   ```
   This will build and start the FastAPI server in a Docker container at `http://localhost:8000`

#### Option 2: Local Python
1. Run FastAPI server directly:
   ```bash
   python3 backend/main.py
   ```
   Must train MLP beforehand.

2. To test the API in a separate terminal:
   ```bash
   python3 backend/test_api.py (path_to_test_video)
   ```

### Running the iOS App
1. Ensure the backend is running (via Docker or locally)
2. Download on iPhone using Xcode (won't work properly on simulator)
3. **If using Docker locally on your Mac:**
   - The app will connect to `http://localhost:8000/analyze` - this only works if running the app on the same machine as Docker
4. **If running the backend on another machine:**
   - Update `ShotAnalysisService.swift` and change `localhost` to your device's LAN address 
