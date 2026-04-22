"""
Data Service - Container Component
Handles storage and retrieval of submission records.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage (in production, use a database like PostgreSQL or MongoDB)
submissions_db = {}

SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5003))


def generate_id():
    """Generate a unique submission ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f"SUB-{timestamp}"


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'data_service',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/submissions', methods=['POST'])
def create_submission():
    """
    Create a new submission record.
    Called by Workflow Service after user submits the form.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Extract required fields
    submission_id = generate_id()
    title = data.get('title', '')
    description = data.get('description', '')
    poster_filename = data.get('poster_filename', '')
    
    # Create initial submission record
    submission_record = {
        'id': submission_id,
        'title': title,
        'description': description,
        'poster_filename': poster_filename,
        'status': 'PENDING',
        'result_note': '',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    # Store the submission
    submissions_db[submission_id] = submission_record
    
    print(f"[Data Service] Created submission: {submission_id}")
    
    return jsonify({
        'success': True,
        'submission_id': submission_id,
        'submission': submission_record
    }), 201


@app.route('/submissions/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    """
    Retrieve a submission record by ID.
    Called by Presentation Service to display results to user.
    """
    submission = submissions_db.get(submission_id)
    
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    return jsonify({
        'success': True,
        'submission': submission
    })


@app.route('/submissions/<submission_id>', methods=['PUT'])
def update_submission(submission_id):
    """
    Update a submission record.
    Called by Result Update Function after processing.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    submission = submissions_db.get(submission_id)
    
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    # Update fields
    if 'status' in data:
        submission['status'] = data['status']
    if 'result_note' in data:
        submission['result_note'] = data['result_note']
    
    submission['updated_at'] = datetime.now().isoformat()
    
    print(f"[Data Service] Updated submission: {submission_id} -> {submission['status']}")
    
    return jsonify({
        'success': True,
        'submission': submission
    })


@app.route('/submissions', methods=['GET'])
def list_submissions():
    """List all submissions (for debugging/admin purposes)"""
    return jsonify({
        'success': True,
        'count': len(submissions_db),
        'submissions': list(submissions_db.values())
    })


if __name__ == '__main__':
    print(f"[Data Service] Starting on port {SERVICE_PORT}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
