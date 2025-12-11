import mediapipe as mp
mp_pose = mp.solutions.pose
import cv2

def normalize(keypoints):
    
    xs = [kp[0] for kp in keypoints]
    ys = [kp[1] for kp in keypoints]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x
    height = max_y - min_y

    return [((x-min_x)/width, (y-min_y)/height, z, v)
            for x,y,z,v in keypoints]

#extract keypoints from image and normalize them, then return them in a list
def extract_keypoints(input):
    poseData = [] #holds keypoints

    pose = mp_pose.Pose(static_image_mode=True, model_complexity=2, min_detection_confidence=0.5)

    img = cv2.imread(input)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    print("Shape:", img_rgb.shape)

    results = pose.process(img_rgb)

    if not results.pose_landmarks:
        print("No pose detected")
    else:
        landmarks = results.pose_landmarks.landmark
        print("Detected", len(landmarks), "landmarks")

    keypoints = []
    for landmark in landmarks:
        keypoints.append((landmark.x, landmark.y, landmark.z, landmark.visibility))
    
    poseData.append(normalize(keypoints))

    return poseData