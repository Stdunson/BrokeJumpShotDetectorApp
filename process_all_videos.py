#runs the video processor on all videos in the "video" folder and saves output to "poseoutput" folder
import os
import subprocess

def process_videos(video_dir, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all video files
    video_extensions = ('.mp4', '.mov', '.MOV', '.MP4', '.avi', '.AVI')
    video_files = [f for f in os.listdir(video_dir) if f.endswith(video_extensions)]
    
    print(f"Found {len(video_files)} videos to process")
    
    # Process each video
    for i, video_file in enumerate(video_files, 1):
        video_path = os.path.join(video_dir, video_file)
        print(f"\nProcessing video {i}/{len(video_files)}: {video_file}")
        
        try:
            # Run the video processor script
            subprocess.run([
                'python3.12',
                'video_processor.py',
                video_path,
                output_dir
            ], check=True)
            print(f"Successfully processed {video_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing {video_file}: {str(e)}")
            continue

if __name__ == "__main__":
    # Define directories
    video_dir = os.path.join(os.getcwd(), "video")
    output_dir = os.path.join(os.getcwd(), "poseoutput")
    
    # Process all videos
    process_videos(video_dir, output_dir)
    print("\nAll videos processed!")