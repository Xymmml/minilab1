"""
Result Update Function - Serverless Component
Updates the stored record with the computed result.

This function is triggered after the Processing Function completes.
It retrieves the result and updates the submission record in the Data Service.
"""

import json
from datetime import datetime


def handler(event, context=None):
    """
    Main handler for the serverless function.
    
    Args:
        event: Processing result containing submission_id and status
        context: Optional context information
    
    Returns:
        dict: Update confirmation
    """
    print(f"[Result Update Function] Received result: {event}")
    
    # Parse event data
    if isinstance(event, str):
        event = json.loads(event)
    
    submission_id = event.get('submission_id')
    status = event.get('status', 'UNKNOWN')
    note = event.get('note', '')
    timestamp = event.get('timestamp', datetime.now().isoformat())
    
    if not submission_id:
        return {
            'error': 'Missing submission_id',
            'status': 'failed'
        }
    
    # In production, this would call the Data Service API
    # For this implementation, the Workflow Service handles the actual update
    # to demonstrate the architectural pattern
    
    update_payload = {
        'submission_id': submission_id,
        'status': status,
        'result_note': note,
        'processed_at': timestamp
    }
    
    print(f"[Result Update Function] Prepared update for: {submission_id}")
    print(f"[Result Update Function] Update payload: {update_payload}")
    
    # Return the update payload
    # The Workflow Service will use this to call the Data Service
    return {
        'success': True,
        'submission_id': submission_id,
        'status': status,
        'note': note,
        'updated_at': datetime.now().isoformat()
    }


# For local testing
if __name__ == '__main__':
    test_result = {
        'submission_id': 'SUB-20240101120000001',
        'status': 'READY',
        'note': 'Your poster has been approved!',
        'timestamp': datetime.now().isoformat()
    }
    
    result = handler(test_result)
    print(f"Update result: {result}")
