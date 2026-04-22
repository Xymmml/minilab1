"""
Test script for the Processing Function
Validates all processing rules.
"""

import sys
sys.path.append('.')

from functions.processing_function.function import handler


def test_missing_fields():
    """Test Rule 1: INCOMPLETE when any required field is missing"""
    test_cases = [
        {
            'submission_id': 'SUB-001',
            'title': '',
            'description': 'Some description with enough characters',
            'poster_filename': 'poster.jpg'
        },
        {
            'submission_id': 'SUB-002',
            'title': 'Test Event',
            'description': '',
            'poster_filename': 'poster.jpg'
        },
        {
            'submission_id': 'SUB-003',
            'title': 'Test Event',
            'description': 'Some description with enough characters',
            'poster_filename': ''
        }
    ]
    
    print("=" * 60)
    print("Test: Missing Fields (Should return INCOMPLETE)")
    print("=" * 60)
    
    all_passed = True
    for i, test in enumerate(test_cases):
        result = handler(test)
        expected = 'INCOMPLETE'
        passed = result['status'] == expected
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        print(f"  Test {i+1}: {status} - Got {result['status']} (expected {expected})")
        if not passed:
            print(f"    Input: title='{test['title']}', desc='{test['description']}', file='{test['poster_filename']}'")
    
    return all_passed


def test_short_description():
    """Test Rule 2a: NEEDS_REVISION when description < 30 chars"""
    test_cases = [
        {
            'submission_id': 'SUB-004',
            'title': 'Test Event',
            'description': 'Too short',
            'poster_filename': 'poster.jpg'
        },
        {
            'submission_id': 'SUB-005',
            'title': 'Another Event',
            'description': 'Exactly 29 chars..........',
            'poster_filename': 'event.png'
        }
    ]
    
    print("\n" + "=" * 60)
    print("Test: Short Description (Should return NEEDS_REVISION)")
    print("=" * 60)
    
    all_passed = True
    for i, test in enumerate(test_cases):
        result = handler(test)
        expected = 'NEEDS_REVISION'
        passed = result['status'] == expected
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        print(f"  Test {i+1}: {status} - Got {result['status']} (expected {expected})")
    
    return all_passed


def test_invalid_extension():
    """Test Rule 2b: NEEDS_REVISION when poster has invalid extension"""
    test_cases = [
        {
            'submission_id': 'SUB-006',
            'title': 'Test Event',
            'description': 'A valid description with more than 30 characters here',
            'poster_filename': 'poster.gif'
        },
        {
            'submission_id': 'SUB-007',
            'title': 'Test Event',
            'description': 'Another valid description with more than 30 characters here',
            'poster_filename': 'poster.bmp'
        },
        {
            'submission_id': 'SUB-008',
            'title': 'Test Event',
            'description': 'Yet another valid description with over 30 characters here',
            'poster_filename': 'document.pdf'
        }
    ]
    
    print("\n" + "=" * 60)
    print("Test: Invalid File Extension (Should return NEEDS_REVISION)")
    print("=" * 60)
    
    all_passed = True
    for i, test in enumerate(test_cases):
        result = handler(test)
        expected = 'NEEDS_REVISION'
        passed = result['status'] == expected
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        print(f"  Test {i+1}: {status} - Got {result['status']} (expected {expected})")
    
    return all_passed


def test_ready():
    """Test Rule 3: READY when all validations pass"""
    test_cases = [
        {
            'submission_id': 'SUB-009',
            'title': 'Tech Conference 2024',
            'description': 'Join us for an amazing tech conference featuring the latest innovations in cloud computing and AI!',
            'poster_filename': 'poster.jpg'
        },
        {
            'submission_id': 'SUB-010',
            'title': 'Art Exhibition',
            'description': 'This is a wonderful art exhibition showcasing talented artists from around the world with diverse styles.',
            'poster_filename': 'artwork.jpeg'
        },
        {
            'submission_id': 'SUB-011',
            'title': 'Music Festival',
            'description': 'Experience three days of incredible live music featuring over 50 artists across multiple stages.',
            'poster_filename': 'festival.png'
        }
    ]
    
    print("\n" + "=" * 60)
    print("Test: Ready for Publication (Should return READY)")
    print("=" * 60)
    
    all_passed = True
    for i, test in enumerate(test_cases):
        result = handler(test)
        expected = 'READY'
        passed = result['status'] == expected
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        print(f"  Test {i+1}: {status} - Got {result['status']} (expected {expected})")
    
    return all_passed


def main():
    print("\n" + "#" * 60)
    print("# Processing Function Unit Tests")
    print("#" * 60)
    
    results = [
        test_missing_fields(),
        test_short_description(),
        test_invalid_extension(),
        test_ready()
    ]
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("ALL TESTS PASSED!")
        return 0
    else:
        print("SOME TESTS FAILED!")
        return 1


if __name__ == '__main__':
    exit(main())
