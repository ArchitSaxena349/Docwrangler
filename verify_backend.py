import requests
import json

BASE_URL = "http://localhost:8000"

def test_backend():
    print("Testing Backend...")
    
    # 1. Health Check
    try:
        resp = requests.get(f"{BASE_URL}/api/health")
        print(f"Health Check: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return

    # 2. Upload File
    try:
        files = {'file': ('test_policy.txt', open('test_policy.txt', 'rb'), 'text/plain')}
        resp = requests.post(f"{BASE_URL}/api/upload", files=files)
        print(f"Upload: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Upload Failed: {e}")
        return

    # 3. Query
    try:
        payload = {"query": "What is the deductible?"}
        resp = requests.post(f"{BASE_URL}/webhook/query", json=payload)
        print(f"Query: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except Exception as e:
        print(f"Query Failed: {e}")

if __name__ == "__main__":
    test_backend()
