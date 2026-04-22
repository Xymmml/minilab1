import json
import os


VALID_EXTENSIONS = (".jpg", ".jpeg", ".png")


def evaluate_submission(title, description, poster_filename):
    """
    Evaluates a submission based on the project rules.
    
    Rules (in order of priority):
    1. If any required field is missing -> INCOMPLETE
    2. Else if description is shorter than 30 characters -> NEEDS REVISION
    3. Else if poster filename does not end with .jpg, .jpeg, or .png -> NEEDS REVISION
    4. Else -> READY
    """
    if not title or not description or not poster_filename:
        return {
            "status": "INCOMPLETE",
            "note": "Required fields are missing.",
        }

    if len(description.strip()) < 30:
        return {
            "status": "NEEDS REVISION",
            "note": "Description must be at least 30 characters.",
        }

    if not poster_filename.lower().endswith(VALID_EXTENSIONS):
        return {
            "status": "NEEDS REVISION",
            "note": "Poster filename must end with .jpg, .jpeg, or .png.",
        }

    return {
        "status": "READY",
        "note": "Submission is complete and ready to share.",
    }


def lambda_handler(event, context):
    """
    AWS Lambda entry point for processing submissions.
    """
    result = evaluate_submission(
        title=event.get("title"),
        description=event.get("description"),
        poster_filename=event.get("poster_filename"),
    )

    return {
        "submission_id": event["submission_id"],
        "title": event.get("title"),
        "description": event.get("description"),
        "poster_filename": event.get("poster_filename"),
        "status": result["status"],
        "note": result["note"],
        "result_update_function_name": event.get(
            "result_update_function_name",
            os.getenv("RESULT_UPDATE_FUNCTION_NAME", "result-update-fn"),
        ),
    }


# Local test
if __name__ == "__main__":
    test_cases = [
        # Case 1: INCOMPLETE (missing field)
        {
            "submission_id": "test-001",
            "title": "Campus Music Night",
            "description": "",
            "poster_filename": "poster.jpg",
        },
        # Case 2: NEEDS REVISION (short description)
        {
            "submission_id": "test-002",
            "title": "Campus Music Night",
            "description": "Short description only",
            "poster_filename": "poster.jpg",
        },
        # Case 3: NEEDS REVISION (invalid extension)
        {
            "submission_id": "test-003",
            "title": "Campus Music Night",
            "description": "A full poster submission for the annual campus music festival.",
            "poster_filename": "poster.gif",
        },
        # Case 4: READY
        {
            "submission_id": "test-004",
            "title": "Campus Music Night",
            "description": "A full poster submission for the annual campus music festival event.",
            "poster_filename": "music-night.png",
        },
    ]
    
    print("=" * 60)
    print("Processing Function Test Cases")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        result = lambda_handler(test, None)
        print(f"\nCase {i}: {result['status']}")
        print(f"  Submission ID: {result['submission_id']}")
        print(f"  Note: {result['note']}")
    
    print("\n" + "=" * 60)
