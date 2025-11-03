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

    def find_best_sequence(self, frame_confidences):
        """Find the best sequence of frames that maintains the correct order: shot pocket -> set point -> follow through"""
        if not all(phase in frame_confidences for phase in ["Shot pocket", "Set point", "Follow through"]):
            return None

        best_sequence = None
        best_sequence_score = -float('inf')
        
        # Get all candidates for each phase
        pocket_frames = [(conf, frame_num, frame) for conf, frame_num, frame in frame_confidences["Shot pocket"]]
        set_frames = [(conf, frame_num, frame) for conf, frame_num, frame in frame_confidences["Set point"]]
        follow_frames = [(conf, frame_num, frame) for conf, frame_num, frame in frame_confidences["Follow through"]]
        
        # Try each combination while respecting temporal order using brute force method
        for pocket_data in pocket_frames:
            pocket_frame_num = pocket_data[1]
            for set_data in set_frames:
                set_frame_num = set_data[1]
                if set_frame_num <= pocket_frame_num:  # Set point must come after shot pocket
                    continue
                for follow_data in follow_frames:
                    follow_frame_num = follow_data[1]
                    if follow_frame_num <= set_frame_num:  # Follow through must come after set point
                        continue
                    
                    # Calculate sequence score (sum of confidences)
                    sequence_score = -sum([pocket_data[0], set_data[0], follow_data[0]])  # Negative because confidences are stored negative
                    
                    if sequence_score > best_sequence_score:
                        best_sequence_score = sequence_score
                        best_sequence = {
                            "Shot pocket": (pocket_data[0], pocket_frame_num, pocket_data[2]),
                            "Set point": (set_data[0], set_frame_num, set_data[2]),
                            "Follow through": (follow_data[0], follow_frame_num, follow_data[2])
                        }
        
        return best_sequence

    def save_best_frames(self, frame_confidences):
        """Save the best sequence of frames maintaining temporal order"""
        best_sequence = self.find_best_sequence(frame_confidences)
        
        if best_sequence is None:
            print("Could not find a complete sequence of shots in the correct order")
            return
        
        # Save frames in order
        for phase, (confidence, frame_num, frame) in best_sequence.items():
            confidence = -confidence  # Convert back to positive
            filename = f"{phase.lower().replace(' ', '_')}_{confidence:.2f}.jpg"
            filepath = os.path.join(self.output_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f"Saved {phase} frame {frame_num} (Confidence: {confidence:.1%}) to {filename}")

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