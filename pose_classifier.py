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
        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
        left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
        head = landmarks[self.mp_pose.PoseLandmark.NOSE]  # Using nose as head reference
        
         #Dominant hand determination, only used for set point & follow through, negligible for shot pocket
        if right_wrist.x < left_wrist.x:
            dominant_wrist = right_wrist
            dominant_elbow = right_elbow
            dominant_shoulder = right_shoulder
        else:
            dominant_wrist = left_wrist
            dominant_elbow = left_elbow
            dominant_shoulder = left_shoulder

        # Calculate elbow angle
        elbow_angle = self.calculate_angle(dominant_wrist, dominant_elbow, dominant_shoulder)

        #calculate wrist heights normalized by body height
        torso_length = abs(right_shoulder.y - right_hip.y)
        wrist_height_norm = (right_wrist.y - right_hip.y) / torso_length
        
        # Calculate relative heights and distances
        wrist_to_head_norm = (dominant_wrist.y - head.y) / torso_length
        elbow_to_head_norm = (dominant_elbow.y - head.y) / torso_length

        # Define ideal values and tolerances (now relative to body proportions)
        IDEAL_SHOT_POCKET_ELBOW = 90.0  
        IDEAL_SET_POINT_ELBOW = 60.0  
        IDEAL_STRAIGHT_ELBOW = 170.0  
        ELBOW_ANGLE_TOLERANCE = 30.0

        #Ideal ranges for three phases elbow angles
        SHOT_POCKET_RANGE = (70, 120)
        SET_POINT_RANGE = (35, 80)
        FOLLOW_THROUGH_RANGE = (150, 185)

        #Normalized set point distance
        shoulder_width = abs(right_shoulder.x - left_shoulder.x)
        shoulder_center_x = (right_shoulder.x + left_shoulder.x) / 2
        wrist_x_offset = abs(dominant_wrist.x - shoulder_center_x) / shoulder_width
        IDEAL_SETPOINT_X = 0.15 
        SETPOINT_TOLERANCE_X = 0.35

        #Ideal vertical distances for shot pocket
        IDEAL_POCKET_WRIST = -0.02
        POCKET_TOLERANCE = 0.25

        #Ideal vertical distances for set point
        IDEAL_SETPOINT_WRIST_HEAD = -0.05 
        SETPOINT_WRIST_HEAD_TOLERANCE = 0.15

        #Ideal vertical distances for follow through wrist height
        IDEAL_FT_WRIST = -0.1 
        FT_TOLERANCE = 0.25

        #Ideal horizontal distances for follow through wrist position
        wrist_forward = dominant_wrist.x - right_elbow.x
        IDEAL_FT_FORWARD = -0.05
        FT_FORWARD_TOLERANCE = 0.15

        # Calculate confidences for each phase
        # Shot pocket confidence - check if elbow angle is within the ideal range
        shot_pocket_in_range = SHOT_POCKET_RANGE[0] <= elbow_angle <= SHOT_POCKET_RANGE[1]
        shot_pocket_elbow_conf = self.calculate_confidence(elbow_angle, IDEAL_SHOT_POCKET_ELBOW, ELBOW_ANGLE_TOLERANCE) if shot_pocket_in_range else 0
        shot_pocket_position_conf = self.calculate_confidence(wrist_height_norm, IDEAL_POCKET_WRIST, POCKET_TOLERANCE)  # Wrist around hip height
        shot_pocket_conf = (shot_pocket_elbow_conf * 0.6 + shot_pocket_position_conf * 0.4)
        
        # Set point confidence - check if elbow angle is within the ideal range
        set_point_in_range = SET_POINT_RANGE[0] <= elbow_angle <= SET_POINT_RANGE[1]
        set_point_elbow_conf = self.calculate_confidence(elbow_angle, IDEAL_SET_POINT_ELBOW, ELBOW_ANGLE_TOLERANCE) if set_point_in_range else 0.2
        set_point_position_conf = self.calculate_confidence(wrist_to_head_norm, IDEAL_SETPOINT_WRIST_HEAD, SETPOINT_WRIST_HEAD_TOLERANCE)  # Slightly above head
        set_point_x_conf = self.calculate_confidence(wrist_x_offset, IDEAL_SETPOINT_X, SETPOINT_TOLERANCE_X)  # Close to head, normalized
        set_point_conf = (set_point_elbow_conf * .25 + set_point_position_conf * .55 + set_point_x_conf * .2)
        
        # Follow through confidence - check if elbow angle is within the ideal range
        follow_through_in_range = FOLLOW_THROUGH_RANGE[0] <= elbow_angle <= FOLLOW_THROUGH_RANGE[1]
        if wrist_to_head_norm > 0:  # If wrist is below head height, zero confidence
            follow_through_conf = 0
        else:
            follow_through_elbow_conf = self.calculate_confidence(elbow_angle, IDEAL_STRAIGHT_ELBOW, ELBOW_ANGLE_TOLERANCE) if follow_through_in_range else 0
            follow_through_wrist_position_conf = self.calculate_confidence(wrist_to_head_norm, IDEAL_FT_WRIST, FT_TOLERANCE)  # Well above head
            follow_through_elbow_position_conf = self.calculate_confidence(elbow_to_head_norm, -0.2, 0.1)  # Above head
            follow_through_forward_conf = self.calculate_confidence(wrist_forward, IDEAL_FT_FORWARD, FT_FORWARD_TOLERANCE)
            follow_through_conf = (follow_through_elbow_conf * 0.4 + follow_through_wrist_position_conf * 0.2 + 
                                 follow_through_elbow_position_conf * 0.2 + follow_through_forward_conf * 0.2)
        
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