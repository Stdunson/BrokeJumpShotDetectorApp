"""
Test script for the broke jumpshot detector backend
Run this after starting the server with: python main.py
Claude Generated
"""

import requests
import sys
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{API_URL}/health"
ANALYZE_ENDPOINT = f"{API_URL}/analyze"


def test_health_check():
    """Test the health check endpoint"""
    print("=" * 60)
    print("Testing Health Check Endpoint")
    print("=" * 60)
    try:
        response = requests.get(HEALTH_ENDPOINT)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Health check passed!\n")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Health check failed: {e}\n")
        return False


def test_video_analysis(video_path):
    """Test the video analysis endpoint"""
    print("=" * 60)
    print("Testing Video Analysis Endpoint")
    print("=" * 60)
    
    # Verify video file exists
    if not Path(video_path).exists():
        print(f"✗ Video file not found: {video_path}\n")
        return False
    
    try:
        with open(video_path, "rb") as f:
            files = {"file": f}
            response = requests.post(ANALYZE_ENDPOINT, files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nAnalysis Results:")
            print(f"  Score: {result['score']}/{result['max_score']}")
            print(f"  Is Broke: {result['is_broke']}")
            print(f"  Message: {result['message']}")
            print(f"\nPhase Results:")
            for phase, data in result['phases'].items():
                prediction = "BUTTER" if data['prediction'] == 1 else "BROKE"
                print(f"  {phase}: {prediction} (confidence: {data['confidence']:.2f})")
            print("\n✓ Video analysis successful!\n")
            return True
        else:
            print(f"✗ Analysis failed: {response.text}\n")
            return False
    
    except Exception as e:
        print(f"✗ Video analysis error: {e}\n")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "BROKE JUMPSHOT DETECTOR - API TESTS" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Test 1: Health check
    health_passed = test_health_check()
    
    # Test 2: Video analysis (if a video path is provided)
    video_analysis_passed = True
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        video_analysis_passed = test_video_analysis(video_path)
    else:
        print("=" * 60)
        print("Video Analysis Test Skipped")
        print("=" * 60)
        print("To test video analysis, provide a video file path:")
        print("  python test_api.py <path_to_video>\n")
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Health Check: {'PASSED ✓' if health_passed else 'FAILED ✗'}")
    print(f"Video Analysis: {'PASSED ✓' if video_analysis_passed else 'SKIPPED' if len(sys.argv) == 1 else 'FAILED ✗'}")
    print()


if __name__ == "__main__":
    main()
