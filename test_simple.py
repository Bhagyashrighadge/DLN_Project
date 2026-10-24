#!/usr/bin/env python3
"""
Simple test script for the Smart Document Assistant API
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TIMEOUT = 60

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*80)
    print("TEST: Health Check")
    print("="*80)
    
    try:
        print(f"Making request to: {API_BASE_URL}/health")
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection refused - is the backend running?")
        print(f"Details: {str(e)}")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\nTesting backend connectivity...")
    if test_health_check():
        print("\n✓ Backend is running!")
    else:
        print("\n✗ Backend is not responding")
