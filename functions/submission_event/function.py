"""
Submission Event Function - Serverless Component
Triggered when a new submission is created.
Converts submission events into processing requests.

In production, this would be deployed as an AWS Lambda, Azure Function,
or Alibaba Cloud Function Compute.
"""

import json
from datetime import datetime


def handler(event, context=None):
    """
    Main handler for the serverless function.
    
    Args:
        event: Event data containing submission_id and submission details
        context: Optional context information
    
    Returns:
        dict: Processing request payload
    """
    print(f"[Submission Event Function] Received event: {event}")
    
    # Parse event data
    if isinstance(event, str):
        event = json.loads(event)
    
    submission_id = event.get('submission_id')
    submission_data = event.get('submission', {})
    
    if not submission_id:
        return {
            'error': 'Missing submission_id',
            'status': 'failed'
        }
    
    # Create processing request
    processing_request = {
        'submission_id': submission_id,
        'title': submission_data.get('title', ''),
        'description': submission_data.get('description', ''),
        'poster_filename': submission_data.get('poster_filename', ''),
        'event_type': 'PROCESSING_REQUESTED',
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"[Submission Event Function] Generated processing request for: {submission_id}")
    
    return processing_request


# For local testing
if __name__ == '__main__':
    test_event = {
        'submission_id': 'SUB-20240101120000001',
        'submission': {
            'title': 'Test Event',
            'description': 'This is a test event description with enough characters',
            'poster_filename': 'test.jpg'
        }
    }
    result = handler(test_event)
    print(f"Test result: {result}")
