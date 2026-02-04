"""Test script for Phase 1 endpoints"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    """Test GET /health"""
    print("1. Testing GET /health")
    print("-" * 50)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("✓ Health check passed\n" if response.status_code == 200 else "✗ Health check failed\n")
    return response.status_code == 200

def test_ingest():
    """Test POST /ingest"""
    print("2. Testing POST /ingest")
    print("-" * 50)
    payload = {
        "text": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents.",
        "title": "AI Introduction",
        "source": "test_doc"
    }
    response = requests.post(f"{BASE_URL}/ingest", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("✓ Ingest endpoint passed\n" if response.status_code == 200 else "✗ Ingest endpoint failed\n")
    return response.status_code == 200

def test_query():
    """Test POST /query"""
    print("3. Testing POST /query")
    print("-" * 50)
    payload = {
        "query": "What is artificial intelligence?",
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("✓ Query endpoint passed\n" if response.status_code == 200 else "✗ Query endpoint failed\n")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Mini RAG API Endpoints - Phase 1")
    print("=" * 50)
    print()
    
    results = []
    results.append(("Health", test_health()))
    results.append(("Ingest", test_ingest()))
    results.append(("Query", test_query()))
    
    print("=" * 50)
    print("Summary:")
    print("=" * 50)
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print()
    if all_passed:
        print("✓ All Phase 1 endpoint tests passed!")
    else:
        print("✗ Some tests failed")
