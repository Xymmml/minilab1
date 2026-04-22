"""Quick test for the services - run each service manually to test"""
import sys
sys.path.insert(0, 'containers/data_service')
sys.path.insert(0, 'containers/workflow_service')
sys.path.insert(0, 'containers/presentation_service')

print("=" * 50)
print("Creator Cloud Studio - Service Test")
print("=" * 50)

# Test 1: Data Service
print("\n[1] Testing Data Service...")
try:
    from containers.data_service.app import app as data_app
    with data_app.test_client() as client:
        response = client.get('/submissions/test')
        print(f"    Data Service: OK (status: {response.status_code})")
except Exception as e:
    print(f"    Data Service: FAILED - {e}")

# Test 2: Workflow Service  
print("\n[2] Testing Workflow Service...")
try:
    from containers.workflow_service.app import app as workflow_app
    with workflow_app.test_client() as client:
        response = client.get('/health')
        print(f"    Workflow Service: OK (status: {response.status_code})")
except Exception as e:
    print(f"    Workflow Service: FAILED - {e}")

# Test 3: Presentation Service
print("\n[3] Testing Presentation Service...")
try:
    from containers.presentation_service.app import app as presentation_app
    with presentation_app.test_client() as client:
        response = client.get('/')
        print(f"    Presentation Service: OK (status: {response.status_code})")
except Exception as e:
    print(f"    Presentation Service: FAILED - {e}")

# Test 4: Processing Function
print("\n[4] Testing Processing Function...")
try:
    from containers.presentation_service.app import app as presentation_app
    # Simulate submission
    test_data = {
        'title': 'Test Event',
        'description': 'This is a test description with enough characters.',
        'poster_filename': 'poster.png'
    }
    response = presentation_app.test_client().post('/api/submit', 
        json=test_data,
        content_type='application/json'
    )
    print(f"    Processing Function: OK (status: {response.status_code})")
    if response.status_code == 200:
        data = response.get_json()
        print(f"    Response: {data}")
except Exception as e:
    print(f"    Processing Function: FAILED - {e}")

print("\n" + "=" * 50)
print("Test Complete!")
print("=" * 50)
