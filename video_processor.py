import cv2
import os
from pose_classifier import PoseClassifier
from collections import defaultdict
import heapq

class VideoProcessor:
    def __init__(self, video_path, output_dir):
        self.video_path = video_path
        self.base_output_dir = output_dir
        self.classifier = PoseClassifier()
        
        # Create base output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a new timestamped folder for this processing session
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        session_folder = f"{video_name}_{timestamp}"
        self.output_dir = os.path.join(output_dir, session_folder)
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Created session folder: {session_folder}")

    def extract_frames(self):
        """Extract frames from video and classify each one"""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"Error opening video file: {self.video_path}")

        frame_confidences = defaultdict(list)  # Dictionary to store frame data for each phase
        frame_number = 0
        
        print("Processing video frames...")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Classify the frame
            results = self.classifier.detect_pose(frame)
            phase, confidence = self.classifier.classify_shot_phase(results)
            
            if phase != "No pose detected" and phase != "Undefined shooting position":
                # Store frame data with negative confidence for max heap (heapq implements min heap)
                frame_data = (-confidence, frame_number, frame)
                frame_confidences[phase].append(frame_data)
            
            frame_number += 1
            if frame_number % 10 == 0:  # Progress update every 10 frames
                print(f"Processed {frame_number} frames")
        
        cap.release()
        return frame_confidences

    def save_best_frames(self, frame_confidences):
        """Save the single best frame for each phase"""
        for phase, frames in frame_confidences.items():
            if not frames:
                continue
                
            # Get the single frame with highest confidence
            best_frame = heapq.nsmallest(1, frames)[0]  # Using smallest because confidences are negative
            confidence = -best_frame[0]  # Convert back to positive
            frame_num = best_frame[1]
            frame = best_frame[2]
            
            # Save the frame
            filename = f"{phase.lower().replace(' ', '_')}_{confidence:.2f}.jpg"
            filepath = os.path.join(self.output_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f"Saved best {phase} frame (Confidence: {confidence:.1%}) to {filename}")

def main():
    import sys
    if len(sys.argv) != 3:
        print("Usage: python video_processor.py <video_path> <output_dir>")
        return
    
    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    processor = VideoProcessor(video_path, output_dir)
    try:
        frame_confidences = processor.extract_frames()
        processor.save_best_frames(frame_confidences)
        print("\nProcessing complete! Check the output directory for the best frames.")
    except Exception as e:
        print(f"Error processing video: {str(e)}")

if __name__ == "__main__":
    main()