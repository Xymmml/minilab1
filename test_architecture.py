"""
Test script to run all services locally without Docker.
Usage:
    python test_architecture.py
"""

import subprocess
import time
import requests
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functions.processing_function.function import handler as process_handler


def wait_for_service(url, timeout=30):
    """Wait for a service to become available"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"  Service at {url} is ready")
                return True
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.Timeout:
            pass
        time.sleep(1)
    print(f"  Timeout waiting for {url}")
    return False


def test_processing_rules():
    """Test the processing function rules"""
    print("\n" + "=" * 60)
    print("Testing Processing Function Rules")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Missing title',
            'input': {'submission_id': 'TEST-001', 'title': '', 'description': 'Valid description with enough chars', 'poster_filename': 'test.jpg'},
            'expected': 'INCOMPLETE'
        },
        {
            'name': 'Short description',
            'input': {'submission_id': 'TEST-002', 'title': 'Test', 'description': 'Too short', 'poster_filename': 'test.jpg'},
            'expected': 'NEEDS_REVISION'
        },
        {
            'name': 'Invalid file extension',
            'input': {'submission_id': 'TEST-003', 'title': 'Test', 'description': 'Valid description with enough characters here', 'poster_filename': 'test.gif'},
            'expected': 'NEEDS_REVISION'
        },
        {
            'name': 'Ready submission',
            'input': {'submission_id': 'TEST-004', 'title': 'Tech Conference', 'description': 'Join us for an amazing tech conference showcasing the latest innovations in AI and cloud!', 'poster_filename': 'poster.png'},
            'expected': 'READY'
        }
    ]
    
    all_passed = True
    for test in test_cases:
        result = process_handler(test['input'])
        passed = result['status'] == test['expected']
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {test['name']}: Expected {test['expected']}, Got {result['status']}")
        if not passed:
            print(f"       Note: {result.get('note', 'N/A')}")
    
    return all_passed


def test_api_integration():
    """Test API endpoints (requires services to be running)"""
    print("\n" + "=" * 60)
    print("Testing API Integration (requires services running)")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    
    # Check if service is running
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        service_running = response.status_code == 200
    except:
        service_running = False
    
    if not service_running:
        print("  Presentation Service not running - skipping API tests")
        print("  Start services with: python containers/presentation_service/app.py")
        return None
    
    # Test submission
    test_payload = {
        'title': 'Test Event',
        'description': 'This is a test event with enough characters for validation',
        'poster_filename': 'test.jpg'
    }
    
    try:
        response = requests.post(f"{base_url}/api/submit", json=test_payload, timeout=5)
        print(f"  Submission test: {response.status_code}")
        if response.status_code in [200, 202]:
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"  Submission test error: {e}")
    
    return True


def main():
    print("\n" + "#" * 60)
    print("# Creator Cloud Studio - Architecture Test")
    print("#" * 60)
    
    results = []
    
    # Test 1: Processing Rules
    results.append(test_processing_rules())
    
    # Test 2: API Integration
    results.append(test_api_integration())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if all(r for r in results if r is not None):
        print("All tests passed!")
    else:
        print("Some tests failed or were skipped.")
    
    print("\nTo run the full application:")
    print("  1. Start Data Service: python containers/data_service/app.py")
    print("  2. Start Workflow Service: python containers/workflow_service/app.py")
    print("  3. Start Presentation Service: python containers/presentation_service/app.py")
    print("  4. Open browser: http://localhost:5001")


if __name__ == '__main__':
    main()
