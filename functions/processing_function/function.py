"""
Processing Function - Serverless Component
Applies validation rules and computes the submission result.

Processing Rules:
1. INCOMPLETE: Any required field is missing
2. NEEDS_REVISION: Description < 30 chars OR poster filename invalid
3. READY: All validations pass
"""

import json
from datetime import datetime


VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
MIN_DESCRIPTION_LENGTH = 30


def handler(event, context=None):
    """
    Main handler for the serverless function.
    
    Args:
        event: Processing request containing submission details
        context: Optional context information
    
    Returns:
        dict: Processing result with status and note
    """
    print(f"[Processing Function] Processing event: {event}")
    
    # Parse event data
    if isinstance(event, str):
        event = json.loads(event)
    
    submission_id = event.get('submission_id')
    title = event.get('title', '')
    description = event.get('description', '')
    poster_filename = event.get('poster_filename', '')
    
    # Apply validation rules
    
    # Rule 1: Check if all required fields are present
    # INCOMPLETE takes highest priority
    missing_fields = []
    
    if not title or title.strip() == '':
        missing_fields.append('title')
    if not description or description.strip() == '':
        missing_fields.append('description')
    if not poster_filename or poster_filename.strip() == '':
        missing_fields.append('poster_filename')
    
    if missing_fields:
        result = {
            'submission_id': submission_id,
            'status': 'INCOMPLETE',
            'note': f'Missing required field(s): {", ".join(missing_fields)}. Please fill in all required fields to proceed.',
            'timestamp': datetime.now().isoformat()
        }
        print(f"[Processing Function] Result: INCOMPLETE - Missing: {missing_fields}")
        return result
    
    # Rule 2: Check if description is at least 30 characters
    if len(description) < MIN_DESCRIPTION_LENGTH:
        result = {
            'submission_id': submission_id,
            'status': 'NEEDS_REVISION',
            'note': f'Description too short ({len(description)}/{MIN_DESCRIPTION_LENGTH} characters). Please provide a more detailed description to help others understand your event.',
            'timestamp': datetime.now().isoformat()
        }
        print(f"[Processing Function] Result: NEEDS_REVISION - Description too short")
        return result
    
    # Rule 3: Check if poster filename has valid extension
    has_valid_extension = any(
        poster_filename.lower().endswith(ext) 
        for ext in VALID_IMAGE_EXTENSIONS
    )
    
    if not has_valid_extension:
        result = {
            'submission_id': submission_id,
            'status': 'NEEDS_REVISION',
            'note': f'Invalid poster format "{poster_filename}". Supported formats: .jpg, .jpeg, .png. Please upload an image in one of these formats.',
            'timestamp': datetime.now().isoformat()
        }
        print(f"[Processing Function] Result: NEEDS_REVISION - Invalid file extension")
        return result
    
    # All checks passed
    result = {
        'submission_id': submission_id,
        'status': 'READY',
        'note': f'Success! Your poster "{title}" has been reviewed and approved. Your event is ready for publication!',
        'timestamp': datetime.now().isoformat()
    }
    print(f"[Processing Function] Result: READY - All validations passed")
    
    return result


# For local testing
if __name__ == '__main__':
    # Test cases
    test_cases = [
        {
            'name': 'Missing fields',
            'event': {
                'submission_id': 'SUB-001',
                'title': '',
                'description': '',
                'poster_filename': ''
            }
        },
        {
            'name': 'Description too short',
            'event': {
                'submission_id': 'SUB-002',
                'title': 'Test Event',
                'description': 'Short',
                'poster_filename': 'poster.jpg'
            }
        },
        {
            'name': 'Invalid file extension',
            'event': {
                'submission_id': 'SUB-003',
                'title': 'Test Event',
                'description': 'A description with enough characters here',
                'poster_filename': 'poster.gif'
            }
        },
        {
            'name': 'Ready for publication',
            'event': {
                'submission_id': 'SUB-004',
                'title': 'Tech Conference 2024',
                'description': 'Join us for an amazing tech conference featuring the latest innovations in cloud computing, AI, and more!',
                'poster_filename': 'conference.png'
            }
        }
    ]
    
    print("=" * 50)
    print("Processing Function Test Cases")
    print("=" * 50)
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Input: {test['event']}")
        result = handler(test['event'])
        print(f"Result: {result['status']}")
        print("-" * 30)
