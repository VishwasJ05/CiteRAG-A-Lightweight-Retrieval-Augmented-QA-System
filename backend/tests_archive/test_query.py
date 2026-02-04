"""Quick test script to query the backend API"""
import requests
import json

# Test query
query = "What is RNN?"

response = requests.post(
    "http://127.0.0.1:8001/query",
    json={"query": query}
)

print(f"Status Code: {response.status_code}")
print(f"\nResponse:")
print(json.dumps(response.json(), indent=2))
