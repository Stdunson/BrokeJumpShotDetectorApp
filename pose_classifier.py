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

    def calculate_confidence(self, measured_value, ideal_value, tolerance):
        """Calculate confidence based on how close a measured value is to the ideal value"""
        difference = abs(measured_value - ideal_value)
        if difference > tolerance:
            return max(0, 1 - (difference - tolerance) / tolerance)
        return 1.0

    def classify_shot_phase(self, results):
        if not results.pose_landmarks:
            return "No pose detected", 0.0

        # Get relevant landmarks
        landmarks = results.pose_landmarks.landmark
        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
        head = landmarks[self.mp_pose.PoseLandmark.NOSE]  # Using nose as head reference
        
        # Calculate elbow angle
        elbow_angle = self.calculate_angle(right_wrist, right_elbow, right_shoulder)
        
        # Calculate relative heights and distances
        wrist_to_hip = right_wrist.y - right_hip.y
        wrist_to_head = right_wrist.y - head.y
        elbow_to_head = right_elbow.y - head.y
        
        # Calculate horizontal distances from head
        wrist_x_distance = abs(right_wrist.x - head.x)  # Distance of wrist from head horizontally
        
        # Define ideal values and tolerances
        IDEAL_BENT_ELBOW = 85.0  # 90 degrees for shot pocket and set point
        IDEAL_STRAIGHT_ELBOW = 170.0  # Nearly straight for follow through
        ELBOW_ANGLE_TOLERANCE = 25.0
        
        # Ideal horizontal distances for set point
        IDEAL_SETPOINT_X_DISTANCE = 0.025  # Wrist should be close to head
        X_DISTANCE_TOLERANCE = 0.05
        
        # Calculate confidences for each phase
        # Shot pocket confidence
        shot_pocket_elbow_conf = self.calculate_confidence(elbow_angle, IDEAL_BENT_ELBOW, ELBOW_ANGLE_TOLERANCE)
        shot_pocket_position_conf = self.calculate_confidence(wrist_to_hip, 0.1, 0.2)  # Slightly above hip
        shot_pocket_conf = (shot_pocket_elbow_conf + shot_pocket_position_conf) / 2
        
        # Set point confidence
        set_point_elbow_conf = self.calculate_confidence(elbow_angle, IDEAL_BENT_ELBOW, ELBOW_ANGLE_TOLERANCE)
        set_point_position_conf = self.calculate_confidence(wrist_to_head, -0.1, 0.05)  # Slightly above head
        set_point_x_conf = self.calculate_confidence(wrist_x_distance, IDEAL_SETPOINT_X_DISTANCE, X_DISTANCE_TOLERANCE)  # Close to head
        set_point_conf = (set_point_elbow_conf + set_point_position_conf + set_point_x_conf) / 3
        
        # Follow through confidence - wrist must be above head, elbow should be above head
        if wrist_to_head > 0:  # If wrist is below head height, zero confidence
            follow_through_conf = 0
        else:
            follow_through_elbow_conf = self.calculate_confidence(elbow_angle, IDEAL_STRAIGHT_ELBOW, ELBOW_ANGLE_TOLERANCE)
            follow_through_wrist_position_conf = self.calculate_confidence(wrist_to_head, -0.3, 0.2)  # Well above head
            follow_through_elbow_position_conf = self.calculate_confidence(elbow_to_head, -0.2, 0.1)  # Above head
            follow_through_conf = (follow_through_elbow_conf + follow_through_wrist_position_conf + 
                                 follow_through_elbow_position_conf) / 3
        
        # Determine phase with highest confidence
        confidences = {
            "Shot pocket": shot_pocket_conf,
            "Set point": set_point_conf,
            "Follow through": follow_through_conf
        }
        
        phase = max(confidences.items(), key=lambda x: x[1])
        confidence = round(phase[1], 2)
        
        if confidence < 0.3:  # If confidence is too low, return undefined
            return "Undefined shooting position", 0.0
            
        return phase[0], confidence

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
    phase, confidence = classifier.classify_shot_phase(results)
    
    # Display the result
    print(f"Detected phase: {phase} (Confidence: {confidence * 100:.1f}%)")
    
    return phase, confidence

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python pose_classifier.py <image_path>")
        return
    
    image_path = sys.argv[1]
    process_image(image_path)

if __name__ == "__main__":
    main()