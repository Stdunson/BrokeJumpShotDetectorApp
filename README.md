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
* To run FastAPI server: python3 backend/main.py
* To run API test script: in a separate terminal: python3 backend/test_api.py (path_to_test_video)
* To run app: download on iPhone using Xcode, won't work properly on simulator. Then, on ShotAnalysisService.swift, put your device's LAN address there instead of "ADDRESS". 