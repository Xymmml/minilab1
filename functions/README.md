# Serverless Functions Configuration

This directory contains the three serverless functions required by the project.

## Functions Overview

### 1. Submission Event Function
- **File**: `submission_event/function.py`
- **Trigger**: Event-driven (submission created)
- **Purpose**: Converts submission events into processing requests

### 2. Processing Function
- **File**: `processing_function/function.py`
- **Trigger**: Event-driven (processing request)
- **Purpose**: Applies validation rules and computes results

### 3. Result Update Function
- **File**: `result_update/function.py`
- **Trigger**: Event-driven (processing complete)
- **Purpose**: Updates stored records with computed results

## Cloud Deployment

### Alibaba Cloud Function Compute (Recommended)

```bash
# Install Funcraft CLI
npm install @alicloud/fun -g

# Configure credentials
fun config

# Deploy all functions
cd functions
fun deploy -t template.yml
```

### AWS Lambda

```bash
# Install AWS CLI and configure credentials
aws configure

# Deploy using SAM
cd functions
aws cloudformation deploy --template-file aws-template.yaml --stack-name poster-submission-functions
```

### Local Testing

Each function includes a `__main__` block for local testing:

```bash
python submission_event/function.py
python processing_function/function.py
python result_update/function.py
```

## Event Schema

### Submission Event
```json
{
  "submission_id": "SUB-20240101120000001",
  "submission": {
    "title": "Event Title",
    "description": "Event description...",
    "poster_filename": "poster.jpg"
  }
}
```

### Processing Request
```json
{
  "submission_id": "SUB-20240101120000001",
  "title": "Event Title",
  "description": "Event description...",
  "poster_filename": "poster.jpg",
  "event_type": "PROCESSING_REQUESTED"
}
```

### Processing Result
```json
{
  "submission_id": "SUB-20240101120000001",
  "status": "READY|NEEDS_REVISION|INCOMPLETE",
  "note": "Result explanation...",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```
