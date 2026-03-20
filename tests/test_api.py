import time
import requests
import subprocess
import json
import os

def test_rest_api():
    print("🚀 Starting FastAPI Server on port 8000...")
    
    # We pipe outputs correctly keeping terminal clean
    server = subprocess.Popen(
        ["python", "-m", "services.api_server"], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    
    try:
        # Give Uvicorn and PyTorch time to spin up their weights natively into memory
        print("⏳ Waiting 30s for ML weights mapping...")
        time.sleep(30)
        
        base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
        video_sample = os.path.join(base_dir, "tests", "videos", "test_video_000_Honduras.mp4")
        
        url = "http://localhost:8000/validate-video"
        payload = {
            "video_path": video_sample,
            "expected_topic": "Honduran football player"
        }
        
        print("📨 Dispatching POST request to /validate-video...")
        start_time = time.time()
        
        response = requests.post(url, json=payload, timeout=300)
        latency = time.time() - start_time
        
        print(f"\n✅ Server Response Status: {response.status_code}")
        print(f"⏱️  Endpoint Latency: {latency:.2f}s")
        print("📝 Response Payload:")
        expected = json.dumps(response.json(), indent=4, ensure_ascii=False)
        print(expected)
        
    except Exception as e:
        print(f"❌ API Test Failed: {e}")
        
    finally:
        print("\n🛑 Shutting down Uvicorn processes...")
        server.terminate()
        server.wait()

if __name__ == "__main__":
    test_rest_api()
