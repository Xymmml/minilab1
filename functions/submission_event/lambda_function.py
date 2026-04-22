import json


def handle_submission_event(event, lambda_client, processing_function_name):
    """
    Handles submission events from SQS.
    Forwards each submission to the Processing Function.
    """
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        lambda_client.invoke(
            FunctionName=processing_function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(body).encode("utf-8"),
        )
    
    return {"message": "submission events forwarded"}


def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    Requires environment variables:
    - PROCESSING_FUNCTION_NAME: Name of the processing function to invoke
    """
    import os
    import boto3
    
    lambda_client = boto3.client("lambda")
    processing_function_name = os.getenv("PROCESSING_FUNCTION_NAME", "processing-fn")
    
    return handle_submission_event(event, lambda_client, processing_function_name)
