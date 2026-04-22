"""
Data Service - Container Component
Handles storage and retrieval of submission records.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage
submissions_db = {}

SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5002))


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


@app.route('/records', methods=['POST'])
def create_record():
    """
    Create a new submission record.
    Called by Workflow Service after user submits the form.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    submission_id = data.get('id', generate_id())
    record = {
        'id': submission_id,
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'poster_filename': data.get('poster_filename', ''),
        'status': data.get('status', 'PENDING'),
        'note': data.get('note', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    submissions_db[submission_id] = record
    print(f"[Data Service] Created record: {submission_id}")
    
    return jsonify(record), 201


@app.route('/records/<record_id>', methods=['GET'])
def get_record(record_id):
    """
    Retrieve a submission record by ID.
    Called by Presentation Service to display results to user.
    """
    record = submissions_db.get(record_id)
    
    if not record:
        return jsonify({'error': 'submission not found'}), 404
    
    return jsonify(record)


@app.route('/records/<record_id>', methods=['PUT'])
def update_record(record_id):
    """
    Update a submission record.
    Called by Result Update Function after processing.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    record = submissions_db.get(record_id)
    
    if not record:
        return jsonify({'error': 'submission not found'}), 404
    
    # Update fields
    if 'status' in data:
        record['status'] = data['status']
    if 'note' in data:
        record['note'] = data['note']
    
    record['updated_at'] = datetime.now().isoformat()
    
    print(f"[Data Service] Updated record: {record_id} -> {record['status']}")
    
    return jsonify(record)


# Backward compatibility aliases
@app.route('/submissions', methods=['POST'])
def create_submission():
    return create_record()


@app.route('/submissions/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    return get_record(submission_id)


@app.route('/submissions/<submission_id>', methods=['PUT'])
def update_submission(submission_id):
    return update_record(submission_id)


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
