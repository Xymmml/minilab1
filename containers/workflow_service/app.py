"""
Workflow Service - Container Component
Orchestrates the submission processing workflow.
Coordinates between Data Service and Serverless Functions.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import threading
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5002))
DATA_SERVICE_URL = os.environ.get('DATA_SERVICE_URL', 'http://localhost:5003')

# For local simulation of serverless functions
PROCESSING_FUNCTION_URL = os.environ.get('PROCESSING_FUNCTION_URL', 'http://localhost:5004')
RESULT_UPDATE_FUNCTION_URL = os.environ.get('RESULT_UPDATE_FUNCTION_URL', 'http://localhost:5005')


def invoke_submission_event_function(submission_id, submission_data):
    """
    Serverless Function 1: Submission Event Function
    Converts a new submission event into a processing request.
    In production, this would trigger an event bus (e.g., AWS EventBridge, Azure Event Grid).
    For local testing, we simulate the call.
    """
    print(f"[Workflow Service] Invoking Submission Event Function for: {submission_id}")
    
    # Simulate event function logic - trigger processing
    event_payload = {
        'submission_id': submission_id,
        'event_type': 'SUBMISSION_CREATED',
        'timestamp': datetime.now().isoformat()
    }
    
    # In production: send to event bus
    # For local: directly call the processing function
    invoke_processing_function(submission_id, submission_data)


def invoke_processing_function(submission_id, submission_data):
    """
    Serverless Function 2: Processing Function
    Applies validation rules and computes the result.
    """
    print(f"[Workflow Service] Invoking Processing Function for: {submission_id}")
    
    # Prepare data for processing
    processing_payload = {
        'submission_id': submission_id,
        'title': submission_data.get('title', ''),
        'description': submission_data.get('description', ''),
        'poster_filename': submission_data.get('poster_filename', '')
    }
    
    try:
        # Call processing function
        # In production: serverless function URL
        # For local: simulate the processing logic
        result = simulate_processing_function(processing_payload)
        
        # Invoke result update function
        invoke_result_update_function(submission_id, result)
        
    except Exception as e:
        print(f"[Workflow Service] Error in processing: {e}")


def simulate_processing_function(payload):
    """
    Simulate the Processing Function logic locally.
    In production, this would be an actual serverless function.
    """
    submission_id = payload['submission_id']
    title = payload.get('title', '')
    description = payload.get('description', '')
    poster_filename = payload.get('poster_filename', '')
    
    print(f"[Processing Function] Evaluating submission: {submission_id}")
    
    # Rule 1: Check if all required fields are present
    missing_fields = []
    if not title or title.strip() == '':
        missing_fields.append('title')
    if not description or description.strip() == '':
        missing_fields.append('description')
    if not poster_filename or poster_filename.strip() == '':
        missing_fields.append('poster_filename')
    
    # INCOMPLETE: Any required field is missing
    if missing_fields:
        result = {
            'status': 'INCOMPLETE',
            'note': f'Missing required field(s): {", ".join(missing_fields)}. Please fill in all required fields.'
        }
        print(f"[Processing Function] Result: INCOMPLETE - {missing_fields}")
        return result
    
    # Rule 2: Check if description is at least 30 characters
    if len(description) < 30:
        result = {
            'status': 'NEEDS_REVISION',
            'note': f'Description too short ({len(description)}/30 chars). Please provide a more detailed description (minimum 30 characters).'
        }
        print(f"[Processing Function] Result: NEEDS_REVISION - Description too short")
        return result
    
    # Rule 3: Check if poster filename has valid extension
    valid_extensions = ['.jpg', '.jpeg', '.png']
    has_valid_extension = any(poster_filename.lower().endswith(ext) for ext in valid_extensions)
    
    if not has_valid_extension:
        result = {
            'status': 'NEEDS_REVISION',
            'note': f'Invalid poster filename "{poster_filename}". Supported formats: .jpg, .jpeg, .png'
        }
        print(f"[Processing Function] Result: NEEDS REVISION - Invalid file extension")
        return result
    
    # All checks passed
    result = {
        'status': 'READY',
        'note': f'Your poster submission "{title}" has been reviewed and is ready for publication!'
    }
    print(f"[Processing Function] Result: READY")
    return result


def invoke_result_update_function(submission_id, result):
    """
    Serverless Function 3: Result Update Function
    Updates the stored record with the computed result.
    """
    print(f"[Workflow Service] Invoking Result Update Function for: {submission_id}")
    
    update_payload = {
        'submission_id': submission_id,
        'status': result['status'],
        'result_note': result['note']
    }
    
    try:
        # Update via Data Service
        update_url = f"{DATA_SERVICE_URL}/submissions/{submission_id}"
        response = requests.put(update_url, json=update_payload)
        
        if response.status_code == 200:
            print(f"[Result Update Function] Successfully updated: {submission_id} -> {result['status']}")
        else:
            print(f"[Result Update Function] Failed to update: {response.text}")
            
    except Exception as e:
        print(f"[Workflow Service] Error updating result: {e}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'workflow_service',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/process', methods=['POST'])
def process_submission():
    """
    Main endpoint to start processing a submission.
    Called by Presentation Service after receiving user input.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Step 1: Create initial submission record via Data Service
    try:
        create_url = f"{DATA_SERVICE_URL}/submissions"
        response = requests.post(create_url, json=data)
        
        if response.status_code != 201:
            return jsonify({'error': 'Failed to create submission', 'details': response.text}), 500
        
        result = response.json()
        submission_id = result['submission_id']
        submission_data = result['submission']
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Data Service unavailable',
            'message': 'Please ensure all services are running'
        }), 503
    
    # Step 2: Trigger background processing via Submission Event Function
    # Run asynchronously to not block the response
    threading.Thread(
        target=invoke_submission_event_function,
        args=(submission_id, submission_data)
    ).start()
    
    print(f"[Workflow Service] Submission {submission_id} queued for processing")
    
    return jsonify({
        'success': True,
        'submission_id': submission_id,
        'message': 'Submission received and processing started'
    }), 202


if __name__ == '__main__':
    print(f"[Workflow Service] Starting on port {SERVICE_PORT}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
