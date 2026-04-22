import os

import requests


def update_result(event, data_service_url):
    """
    Updates the submission record in the Data Service with the final result.
    """
    response = requests.put(
        f"{data_service_url}/records/{event['submission_id']}",
        json={
            "status": event["status"],
            "note": event["note"],
        },
        timeout=10,
    )
    response.raise_for_status()
    return {
        "message": "result updated",
        "submission_id": event["submission_id"],
        "status": event["status"],
        "note": event["note"],
    }


def lambda_handler(event, context):
    """
    AWS Lambda entry point for updating results.
    Requires:
    - data_service_url: URL of the Data Service (from event or environment)
    """
    data_service_url = event.get("data_service_url") or os.getenv(
        "DATA_SERVICE_URL",
        "http://data-service:5002",
    )
    return update_result(event, data_service_url)
