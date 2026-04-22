"""
Local Lambda Runner

Simulates AWS Lambda invocation for local development.
This allows testing the full workflow without AWS deployment.
"""

import importlib.util
import json
import threading
from io import BytesIO
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def load_lambda_module(relative_dir_name):
    """Load a Lambda function module from the functions directory."""
    module_path = BASE_DIR / "functions" / relative_dir_name / "lambda_function.py"
    spec = importlib.util.spec_from_file_location(relative_dir_name.replace("-", "_"), module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


submission_event_module = load_lambda_module("submission_event")
processing_module = load_lambda_module("processing_function")
result_update_module = load_lambda_module("result_update")


class FakePayload(BytesIO):
    """Mock AWS Lambda response payload."""
    pass


class LocalLambdaClient:
    """
    Simulates AWS Lambda client for local invocation.
    Used by submission_event Lambda to call processing and result_update functions.
    """
    
    def __init__(self, data_service_url, processing_function_name, result_update_function_name):
        self.data_service_url = data_service_url
        self.processing_function_name = processing_function_name
        self.result_update_function_name = result_update_function_name

    def invoke(self, FunctionName, InvocationType, Payload):
        payload = json.loads(Payload.decode("utf-8"))

        if FunctionName == self.processing_function_name:
            # Call Processing Function
            result = processing_module.lambda_handler(payload, None)
            # Then call Result Update Function
            self.invoke(
                FunctionName=self.result_update_function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(
                    {
                        **result,
                        "data_service_url": self.data_service_url,
                    }
                ).encode("utf-8"),
            )
            return {"StatusCode": 200, "Payload": FakePayload(json.dumps(result).encode("utf-8"))}

        if FunctionName == self.result_update_function_name:
            # Call Result Update Function
            result = result_update_module.lambda_handler(payload, None)
            return {"StatusCode": 200, "Payload": FakePayload(json.dumps(result).encode("utf-8"))}

        raise ValueError(f"Unsupported local function: {FunctionName}")


def run_local_event_chain(message, data_service_url, processing_function_name, result_update_function_name):
    """
    Runs the complete event chain locally.
    Simulates: Submission Event -> Processing -> Result Update
    """
    event = {"Records": [{"body": json.dumps(message)}]}
    lambda_client = LocalLambdaClient(
        data_service_url=data_service_url,
        processing_function_name=processing_function_name,
        result_update_function_name=result_update_function_name,
    )
    submission_event_module.handle_submission_event(
        event,
        lambda_client=lambda_client,
        processing_function_name=processing_function_name,
    )


def start_background_processing(message, data_service_url, processing_function_name, result_update_function_name):
    """
    Starts the background processing in a separate thread.
    Called by workflow_service when LOCAL_ASYNC_MODE is enabled.
    """
    worker = threading.Thread(
        target=run_local_event_chain,
        args=(message, data_service_url, processing_function_name, result_update_function_name),
        daemon=True,
    )
    worker.start()
