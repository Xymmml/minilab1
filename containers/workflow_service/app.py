"""
Workflow Service - Container Component
Coordinates the submission workflow and triggers background processing.
"""

import json
import os
import uuid

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://data-service:5002")
SUBMISSION_QUEUE_URL = os.getenv("SUBMISSION_QUEUE_URL", "local-submission-queue")
LOCAL_ASYNC_MODE = os.getenv("LOCAL_ASYNC_MODE", "true").lower() == "true"
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
PROCESSING_FUNCTION_NAME = os.getenv("PROCESSING_FUNCTION_NAME", "processing-fn")
RESULT_UPDATE_FUNCTION_NAME = os.getenv("RESULT_UPDATE_FUNCTION_NAME", "result-update-fn")


def build_submission_event(submission_id, title, description, poster_filename):
    """Build the submission event payload for Lambda invocation."""
    return {
        "submission_id": submission_id,
        "title": title,
        "description": description,
        "poster_filename": poster_filename,
        "result_update_function_name": RESULT_UPDATE_FUNCTION_NAME,
    }


def trigger_background_processing(submission_event):
    """
    Triggers background processing either via local runner or AWS SQS.
    """
    if LOCAL_ASYNC_MODE:
        # Use local runner for development
        from local_runner import start_background_processing
        start_background_processing(
            message=submission_event,
            data_service_url=DATA_SERVICE_URL,
            processing_function_name=PROCESSING_FUNCTION_NAME,
            result_update_function_name=RESULT_UPDATE_FUNCTION_NAME,
        )
    else:
        # Use AWS SQS in production
        import boto3
        sqs_client = boto3.client("sqs", region_name=AWS_REGION)
        sqs_client.send_message(
            QueueUrl=SUBMISSION_QUEUE_URL,
            MessageBody=json.dumps(submission_event),
        )


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/submit", methods=["POST"])
def submit():
    """
    Accepts a poster submission, creates a record, and triggers background processing.
    """
    payload = request.get_json(force=True)

    submission_id = str(uuid.uuid4())
    record = {
        "id": submission_id,
        "title": payload.get("title", ""),
        "description": payload.get("description", ""),
        "poster_filename": payload.get("poster_filename", ""),
        "status": "PENDING",
        "note": "Submission received and queued for background processing.",
    }

    submission_event = build_submission_event(
        submission_id=submission_id,
        title=record["title"],
        description=record["description"],
        poster_filename=record["poster_filename"],
    )

    # Create initial record in Data Service
    create_response = requests.post(
        f"{DATA_SERVICE_URL}/records",
        json=record,
        timeout=10,
    )
    create_response.raise_for_status()

    # Trigger background processing
    trigger_background_processing(submission_event)

    return jsonify({"submission_id": submission_id, "status": "PENDING"}), 202


@app.route("/result/<submission_id>", methods=["GET"])
def get_result(submission_id):
    """Retrieve the result of a submission."""
    response = requests.get(f"{DATA_SERVICE_URL}/records/{submission_id}", timeout=10)

    if response.status_code == 404:
        return jsonify({"error": "submission not found"}), 404

    response.raise_for_status()
    return jsonify(response.json())


if __name__ == "__main__":
    print(f"[Workflow Service] Starting on port 5001")
    app.run(host="0.0.0.0", port=5001)
