#FastAPI backend for Broke Jumpshot Detector

import os
import sys
import tempfile
import shutil
import numpy as np
import cv2
import torch
import torch.nn as nn
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
import mediapipe as mp
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

load_dotenv()

#Parent directory for model import
sys.path.insert(0, str(Path(__file__).parent.parent))
from pose_classifier import PoseClassifier
from video_processor import VideoProcessor

#Global variables
model = None
device = None
pose_classifier = None
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10/minute"]
)


#Environment variables
MODEL_WEIGHTS_PATH = os.getenv("MODEL_WEIGHTS_PATH")
API_KEY = os.getenv("API_KEY")
MAX_VIDEO_MB = int(os.getenv("MAX_VIDEO_MB", "25"))

class PoseMLP(nn.Module):
    def __init__(self, input_dim=135, hidden_dim1=128, hidden_dim2=64, dropout=0.2, output_dim=1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.BatchNorm1d(hidden_dim1),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim1, hidden_dim2),
            nn.BatchNorm1d(hidden_dim2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim2, output_dim)
        )
    
    def forward(self, x):
        return self.net(x).squeeze(-1)


#Initialize FastAPI app with lifespan and model loading
async def lifespan(app: FastAPI):
    global model, device, pose_classifier
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    try:
        pose_classifier = PoseClassifier()
        print("Initialized PoseClassifier")
    except Exception as e:
        print(f"Error initializing PoseClassifier: {e}")
        pose_classifier = None
    
    default_weights_path = Path(__file__).parent.parent / "MLweights" / "broke_jump_shot_detector_weights_v5.pth"

    weights_path = Path(os.getenv("MODEL_WEIGHTS_PATH", default_weights_path))

    if not weights_path.exists():
        print(f"Warning: Model weights not found at {weights_path}")
        model = None
    else:
        try:
            model = PoseMLP(input_dim=135, hidden_dim1=128, hidden_dim2=64, dropout=0.2, output_dim=1)
            model = model.to(device)
            
            state_dict = torch.load(weights_path, map_location=device, weights_only=True)
            model.load_state_dict(state_dict)
            model.eval()
            print(f"Loaded model weights from {weights_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            model = None
    
    yield
    
    print("Shutting down...")


app = FastAPI(
    title="Broke Jumpshot Detector API",
    version="1.0.0",
    lifespan=lifespan
)

#Rate Limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

#Helper Functions from pose_classifier.py
def extract_frames_from_video(video_path: str, num_frames: int = 3) -> list:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        raise ValueError("Video has no frames")
    
    # Sample frames evenly across the video
    frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
    frames = []
    
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            timestamp = idx / fps
            frames.append((frame, timestamp, idx))
    
    cap.release()
    
    if not frames:
        raise ValueError("No frames extracted from video")
    
    return frames


def detect_pose(frame, pose_detector):
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose_detector.detect_pose(image_rgb)
    
    if not results or not results.pose_landmarks:
        return None
    
    return results


def extract_keypoints(results) -> np.ndarray:
    if not results or not results.pose_landmarks:
        return None
    
    keypoints = []
    for landmark in results.pose_landmarks.landmark:
        keypoints.append([landmark.x, landmark.y, landmark.z, landmark.visibility])
    
    return np.array(keypoints, dtype=np.float32).flatten()


def get_shot_phase(results) -> tuple:
    if pose_classifier is None or not results:
        return "unknown", 0.0
    
    phase, confidence = pose_classifier.classify_shot_phase(results)
    return phase, confidence


def predict_shot_quality(keypoints: np.ndarray) -> tuple:
    if model is None:
        return None, 0.0
    
    with torch.no_grad():
        input_tensor = torch.tensor(keypoints, dtype=torch.float32).to(device)
        
        logit = model(input_tensor.unsqueeze(0)).squeeze()
        
        prob = torch.sigmoid(logit).cpu().item()
        
        prediction = 1 if prob > 0.5 else 0
        confidence = max(prob, 1 - prob)
    
    return prediction, confidence

#Helper function to select best frames based on VideoProcessor logic
def select_best_frames_from_video(video_path: str, output_dir: Path = None) -> list:
    try:
        # Use VideoProcessor to extract and analyze all frames
        vp = VideoProcessor(video_path, str(output_dir or tempfile.gettempdir()))
        frames_data = vp.extract_frames(sample_rate=1)
        
        # Get the best sequence
        sequence = vp.find_best_sequence(max_candidates=8)
        
        if sequence is None:
            return None
        
        # Extract frames from sequence
        best_frames = []
        kind, data = sequence
        
        if kind == "triplet":
            for phase_key in ["pocket", "set", "ft"]:
                candidate = data[phase_key]
                frame = candidate["frame"]
                frame_idx = candidate["frame_idx"]
                conf = candidate["conf"]
                phase_name = "shot pocket" if phase_key == "pocket" else ("set point" if phase_key == "set" else "follow through")
                best_frames.append((frame, phase_name, frame_idx, conf))
        
        elif kind == "pair":
            pair_type, payload = data  # Unpack the nested tuple
            for label, candidate in payload.items():
                if label != "score":
                    frame = candidate["frame"]
                    frame_idx = candidate["frame_idx"]
                    conf = candidate["conf"]
                    phase_name = label.replace("_", " ")
                    best_frames.append((frame, phase_name, frame_idx, conf))
        
        elif kind == "single":
            candidate = data["single"]
            frame = candidate["frame"]
            frame_idx = candidate["frame_idx"]
            conf = candidate["conf"]
            best_frames.append((frame, "unknown", frame_idx, conf))
        
        return best_frames
    
    except Exception as e:
        print(f"Error in select_best_frames_from_video: {e}")
        return None


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(device)
    }

#Uses ML model to classify each phase
@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze_video(request: Request, file: UploadFile = File(...)):
    
    if request.headers.get("X-API-KEY") != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid video format. Supported: mp4, mov, avi, mkv")
    
    temp_dir = tempfile.mkdtemp()
    temp_video_path = os.path.join(temp_dir, file.filename)
    
    try:
        contents = await file.read()

        if len(contents) > MAX_VIDEO_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"Video file size exceeds the maximum limit of {MAX_VIDEO_MB} MB")

        with open(temp_video_path, "wb") as f:
            f.write(contents)
        
        results_dir = Path(temp_dir) / "results"
        results_dir.mkdir(exist_ok=True)
        
        best_frames = select_best_frames_from_video(temp_video_path, results_dir)
        
        results = {
            "shot_pocket": {"prediction": None, "confidence": 0.0, "phase": "shot pocket"},
            "set_point": {"prediction": None, "confidence": 0.0, "phase": "set point"},
            "follow_through": {"prediction": None, "confidence": 0.0, "phase": "follow through"}
        }
        
        phase_mapping = {
            "shot pocket": "shot_pocket",
            "set point": "set_point",
            "follow through": "follow_through"
        }
        
        # If best frames found, process them; otherwise all phases default to 0 (broke)
        if best_frames:
            # Process each selected frame
            for i, (frame, phase_name, frame_idx, phase_confidence) in enumerate(best_frames):
                pose_results = detect_pose(frame, pose_classifier)
                if pose_results is None:
                    print(f"Warning: No pose detected in selected frame {i} ({phase_name})")
                    continue
                
                keypoints = extract_keypoints(pose_results)
                if keypoints is None:
                    continue
                
                phase_vector = np.zeros(3, dtype=np.float32)
                phase_idx = {"shot pocket": 0, "set point": 1, "follow through": 2}.get(phase_name, 0)
                phase_vector[phase_idx] = 1.0
                
                input_vector = np.concatenate([keypoints, phase_vector])
                
                prediction, confidence = predict_shot_quality(input_vector)
                
                if prediction is not None:
                    phase_key = phase_mapping.get(phase_name, "shot_pocket")
                    results[phase_key]["prediction"] = int(prediction)
                    results[phase_key]["confidence"] = float(confidence)
                    results[phase_key]["phase_name"] = phase_name
                    results[phase_key]["phase_confidence"] = float(phase_confidence)
                    
                    frame_filename = f"{phase_key}_{frame_idx}_conf{confidence:.2f}.jpg"
                    frame_path = results_dir / frame_filename
                    cv2.imwrite(str(frame_path), frame)
                    results[phase_key]["saved_frame"] = frame_filename
        else:
            # No best frames found, default all phases to prediction 0 (broke)
            print("Warning: No best frames selected from video, defaulting all phases to broke (0)")
            for phase_key in results.keys():
                results[phase_key]["prediction"] = 0
                results[phase_key]["confidence"] = 0.0
        
        score = 0
        broke_phases = []
        
        if results["shot_pocket"]["prediction"] == 1:
            score += 2
        else:
            broke_phases.append("shot pocket")
        
        if results["set_point"]["prediction"] == 1:
            score += 3
        else:
            broke_phases.append("set point")
        
        if results["follow_through"]["prediction"] == 1:
            score += 4
        else:
            broke_phases.append("follow through")
        
        is_broke = score < 9
        
        if is_broke:
            feedback = f"Shot is BROKE. Score: {score}/9. "
            if len(broke_phases) == 3:
                feedback += "All phases need improvement."
            else:
                feedback += f"Improve: {', '.join(broke_phases)}."
        else:
            feedback = f"Shot is BUTTER! Score: {score}/9. Good form!"
        
        return JSONResponse({
            "score": score,
            "is_broke": is_broke,
            "max_score": 9,
            "phases": results,
            "message": feedback,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing video: {str(e)}")
    
    finally:
        # Remove temporary files and directories
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
