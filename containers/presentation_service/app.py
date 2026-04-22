"""
Presentation Service - Container Component
Accepts user submissions and displays final results.
This is the main user-facing interface of the application.
"""

from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_cors import CORS
import os
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5001))
WORKFLOW_SERVICE_URL = os.environ.get('WORKFLOW_SERVICE_URL', 'http://localhost:5002')
DATA_SERVICE_URL = os.environ.get('DATA_SERVICE_URL', 'http://localhost:5003')

# Simple HTML template for the form
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Creator Cloud Studio - Poster Submission</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 8px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        input, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e1e1;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        .hint {
            font-size: 12px;
            color: #888;
            margin-top: 4px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 12px;
            display: none;
        }
        .result.show {
            display: block;
        }
        .result.ready {
            background: #d4edda;
            border: 2px solid #28a745;
        }
        .result.needs-revision {
            background: #fff3cd;
            border: 2px solid #ffc107;
        }
        .result.incomplete {
            background: #f8d7da;
            border: 2px solid #dc3545;
        }
        .result h3 {
            margin-bottom: 10px;
            font-size: 18px;
        }
        .result p {
            color: #333;
            line-height: 1.6;
        }
        .status-badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .status-ready { background: #28a745; color: white; }
        .status-needs-revision { background: #ffc107; color: #333; }
        .status-incomplete { background: #dc3545; color: white; }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .loading.show { display: block; }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Creator Cloud Studio</h1>
        <p class="subtitle">Submit your event poster for review</p>
        
        <form id="submissionForm">
            <div class="form-group">
                <label for="title">Event Title *</label>
                <input type="text" id="title" name="title" placeholder="Enter event title" required>
            </div>
            
            <div class="form-group">
                <label for="description">Description *</label>
                <textarea id="description" name="description" placeholder="Describe your event (minimum 30 characters)" required></textarea>
                <p class="hint" id="descHint">0/30 characters minimum</p>
            </div>
            
            <div class="form-group">
                <label for="poster_filename">Poster Image Filename *</label>
                <input type="text" id="poster_filename" name="poster_filename" placeholder="e.g., poster.jpg" required>
                <p class="hint">Supported formats: .jpg, .jpeg, .png</p>
            </div>
            
            <button type="submit" id="submitBtn">Submit Poster</button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Submitting your poster...</p>
        </div>
        
        <div class="result" id="result"></div>
    </div>
    
    <script>
        const form = document.getElementById('submissionForm');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');
        const submitBtn = document.getElementById('submitBtn');
        const descInput = document.getElementById('description');
        const descHint = document.getElementById('descHint');
        
        descInput.addEventListener('input', function() {
            const len = this.value.length;
            descHint.textContent = len < 30 ? `${len}/30 characters minimum` : `${len} characters (OK)`;
            descHint.style.color = len >= 30 ? '#28a745' : '#888';
        });
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;
            const poster_filename = document.getElementById('poster_filename').value;
            
            form.style.display = 'none';
            loading.classList.add('show');
            
            try {
                const response = await fetch('/api/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, description, poster_filename })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Poll for result
                    checkResult(data.submission_id);
                } else {
                    showError(data.error || 'Submission failed');
                }
            } catch (error) {
                showError('Network error. Please try again.');
            }
        });
        
        async function checkResult(submissionId) {
            const maxAttempts = 20;
            let attempts = 0;
            
            const poll = async () => {
                try {
                    const response = await fetch(`/api/submissions/${submissionId}`);
                    const data = await response.json();
                    
                    if (data.submission && data.submission.status !== 'PENDING') {
                        showResult(data.submission);
                        return;
                    }
                    
                    attempts++;
                    if (attempts < maxAttempts) {
                        setTimeout(poll, 500);
                    } else {
                        showError('Processing timeout. Please try again.');
                    }
                } catch (error) {
                    attempts++;
                    if (attempts < maxAttempts) {
                        setTimeout(poll, 500);
                    }
                }
            };
            
            poll();
        }
        
        function showResult(submission) {
            loading.classList.remove('show');
            result.classList.add('show');
            
            let statusClass = 'ready';
            let statusText = submission.status;
            
            if (submission.status === 'READY') {
                statusClass = 'ready';
            } else if (submission.status === 'NEEDS_REVISION') {
                statusClass = 'needs-revision';
            } else if (submission.status === 'INCOMPLETE') {
                statusClass = 'incomplete';
            }
            
            result.innerHTML = `
                <span class="status-badge status-${statusClass}">${statusText}</span>
                <p>${submission.result_note}</p>
                <p style="margin-top: 10px; font-size: 12px; color: #666;">
                    Submission ID: ${submission.id}
                </p>
            `;
        }
        
        function showError(message) {
            loading.classList.remove('show');
            form.style.display = 'block';
            alert(message);
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve the main submission form"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'presentation_service',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/submit', methods=['POST'])
def submit_poster():
    """
    Accept user submission and forward to Workflow Service.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['title', 'description', 'poster_filename']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'error': f'Missing required field: {field}'
            }), 400
    
    try:
        # Forward to Workflow Service
        workflow_url = f"{WORKFLOW_SERVICE_URL}/process"
        response = requests.post(workflow_url, json=data, timeout=5)
        
        if response.status_code == 202:
            result = response.json()
            return jsonify(result)
        else:
            return jsonify({
                'error': 'Workflow processing failed',
                'details': response.text
            }), 500
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Service temporarily unavailable',
            'message': 'Please try again later'
        }), 503


@app.route('/api/submissions/<submission_id>', methods=['GET'])
def get_submission_status(submission_id):
    """
    Get submission status from Data Service.
    """
    try:
        data_url = f"{DATA_SERVICE_URL}/submissions/{submission_id}"
        response = requests.get(data_url)
        
        if response.status_code == 200:
            return jsonify(response.json())
        elif response.status_code == 404:
            return jsonify({'error': 'Submission not found'}), 404
        else:
            return jsonify({'error': 'Failed to retrieve submission'}), 500
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Data Service unavailable'
        }), 503


if __name__ == '__main__':
    print(f"[Presentation Service] Starting on port {SERVICE_PORT}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
