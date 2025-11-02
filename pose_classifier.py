import cv2
import mediapipe as mp
import numpy as np
import ssl

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

class PoseClassifier:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            min_detection_confidence=0.5
        )

    def detect_pose(self, image):
        # Convert the BGR image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        return results

    def calculate_angle(self, a, b, c):
        """Calculate the angle between three points"""
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)

    def classify_shot_phase(self, results):
        if not results.pose_landmarks:
            return "No pose detected"

        # Get relevant landmarks
        landmarks = results.pose_landmarks.landmark
        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
        head = landmarks[self.mp_pose.PoseLandmark.NOSE]  # Using nose as head reference
        
        # Calculate elbow angle
        elbow_angle = self.calculate_angle(right_wrist, right_elbow, right_shoulder)
        
        # Calculate relative positions
        wrist_height = right_wrist.y
        head_height = head.y
        elbow_height = right_elbow.y
        hip_height = right_hip.y
        
        # Define thresholds
        BENT_ELBOW_MAX = 120  # Angle less than this means elbow is bent
        STRAIGHT_ELBOW_MIN = 150  # Angle more than this means elbow is straight
        
        # Shot pocket detection (elbows bent and near hips)
        if (elbow_angle < BENT_ELBOW_MAX and 
            abs(wrist_height - hip_height) < 0.5):
            return "Shot pocket"
        
        # Set point detection (elbows bent and near head)
        elif (elbow_angle < BENT_ELBOW_MAX and 
              abs(elbow_height - head_height) < 0.5 and 
              abs(wrist_height - head_height) < 0.5):
            return "Set point"
        
        # Follow through detection (elbows straight and above head)
        elif (elbow_angle > STRAIGHT_ELBOW_MIN and 
              wrist_height < head_height and 
              elbow_height < head_height):
            return "Follow through"
        
        return "Undefined shooting position"

def process_image(image_path):
    # Initialize classifier
    classifier = PoseClassifier()
    
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to read image: {image_path}")
        return
    
    # Detect and classify pose
    results = classifier.detect_pose(image)
    phase = classifier.classify_shot_phase(results)
    
    # Display the result
    print(f"Detected phase: {phase}")
    
    return phase

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python pose_classifier.py <image_path>")
        return
    
    image_path = sys.argv[1]
    process_image(image_path)

if __name__ == "__main__":
    main()