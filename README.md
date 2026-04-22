# Creator Cloud Studio

Creator Cloud Studio is a small hybrid cloud mini-project for event poster submission processing. The system deliberately combines **3 container services** and **3 serverless functions** to satisfy the required workflow:

`user submits input -> workflow creates record -> event function starts processing -> processing function produces outcome -> result function updates system -> user views result`

## 1. Project Directory Structure

```
mini-project-1/
├── containers/
│   ├── presentation_service/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── workflow_service/
│   │   ├── app.py
│   │   ├── local_runner.py          # Local Lambda simulation
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── data_service/
│       ├── app.py
│       ├── requirements.txt
│       └── Dockerfile
├── functions/
│   ├── submission_event/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   ├── processing_function/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   └── result_update/
│       ├── lambda_function.py
│       └── requirements.txt
├── docker-compose.yml
└── README.md
```

## 2. Architecture Overview

### The 6 Required Components

#### Container-based Services

1. **Presentation Service** (Port 5000)
   - Flask web UI
   - Displays the submission form
   - Displays the final result

2. **Workflow Service** (Port 5001)
   - Receives submission API calls
   - Creates the initial record with `PENDING`
   - Sends a submission event to the asynchronous processing path

3. **Data Service** (Port 5002)
   - Stores and retrieves submission records
   - Exposes `POST /records`, `GET /records/<id>`, `PUT /records/<id>`

#### Serverless Functions

1. **Submission Event Function**
   - Triggered by SQS
   - Reads the submission event
   - Invokes the Processing Function

2. **Processing Function**
   - Applies the assignment rules
   - Produces the final status and note

3. **Result Update Function**
   - Writes the final status and note back to the Data Service

### Why This is a Hybrid Cloud Application

- The UI, workflow API, and data API are long-running HTTP services, so they are implemented as **containers on ECS Fargate**.
- The validation pipeline is event-driven and short-lived, so it is implemented as **AWS Lambda serverless functions**.
- This split clearly shows different execution models inside one application.

### Event-Driven Workflow

```
Browser
  -> Presentation Service (Port 5000)
  -> Workflow Service (Port 5001)
  -> Data Service creates PENDING record
  -> SQS submission queue
  -> Submission Event Lambda
  -> Processing Lambda
  -> Result Update Lambda
  -> Data Service updates record
  -> Presentation Service shows final status
```

## 3. Business Rules Implemented

The logic in `processing_function/lambda_function.py` strictly follows the required priority:

1. If any required field is missing -> `INCOMPLETE`
2. Else if description is shorter than 30 characters -> `NEEDS REVISION`
3. Else if poster filename does not end with `.jpg`, `.jpeg`, or `.png` -> `NEEDS REVISION`
4. Else -> `READY`

Returned notes:

- `Required fields are missing.`
- `Description must be at least 30 characters.`
- `Poster filename must end with .jpg, .jpeg, or .png.`
- `Submission is complete and ready to share.`

## 4. Container Service APIs

### Data Service (Port 5002)

- `POST /records`
- `GET /records/<id>`
- `PUT /records/<id>`
- `GET /health`

Record fields: `id`, `title`, `description`, `poster_filename`, `status`, `note`

### Workflow Service (Port 5001)

- `POST /submit`
- `GET /result/<id>`
- `GET /health`

### Presentation Service (Port 5000)

- `GET /`
- `POST /submit`
- `GET /result/<id>`

## 5. Local Development

The local version uses Docker Compose for the 3 Flask container services only.

Because Lambda and SQS are AWS-managed services, local testing uses a **local async simulator** inside `workflow_service/local_runner.py`:

- Workflow Service still creates the record first
- Workflow Service still emits a submission event object
- The event is processed asynchronously in a background thread
- The thread calls the 3 Lambda handlers in the same order as AWS

This keeps the local demo small while preserving the same component boundaries and event-driven workflow.

### Run Locally

```bash
docker-compose up --build
```

Open:

- Presentation UI: [http://localhost:5000](http://localhost:5000)
- Workflow API: [http://localhost:5001](http://localhost:5001)
- Data API: [http://localhost:5002](http://localhost:5002)

### Local Test Cases

#### Case 1: INCOMPLETE

- Title: `Campus Music Night`
- Description: leave blank
- Poster Filename: `poster.jpg`

Expected result:

- Final Status: `INCOMPLETE`
- Note: `Required fields are missing.`

#### Case 2: NEEDS REVISION

- Title: `Campus Music Night`
- Description: `Short description only`
- Poster Filename: `poster.jpg`

Expected result:

- Final Status: `NEEDS REVISION`
- Note: `Description must be at least 30 characters.`

#### Case 3: NEEDS REVISION (Invalid Extension)

- Title: `Campus Music Night`
- Description: `A full poster submission for the annual campus music festival.`
- Poster Filename: `poster.gif`

Expected result:

- Final Status: `NEEDS REVISION`
- Note: `Poster filename must end with .jpg, .jpeg, or .png.`

#### Case 4: READY

- Title: `Campus Music Night`
- Description: `A full poster submission for the annual campus music festival event.`
- Poster Filename: `music-night.png`

Expected result:

- Final Status: `READY`
- Note: `Submission is complete and ready to share.`

## 6. AWS Deployment

### 6.1 Build and Push the 3 Container Services to Amazon ECR

Create three ECR repositories:

```bash
aws ecr create-repository --repository-name creator-cloud-studio-presentation
aws ecr create-repository --repository-name creator-cloud-studio-workflow
aws ecr create-repository --repository-name creator-cloud-studio-data
```

Build and push:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -f containers/presentation_service/Dockerfile -t creator-cloud-studio-presentation .
docker build -f containers/workflow_service/Dockerfile -t creator-cloud-studio-workflow .
docker build -f containers/data_service/Dockerfile -t creator-cloud-studio-data .

docker tag creator-cloud-studio-presentation:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/creator-cloud-studio-presentation:latest
docker tag creator-cloud-studio-workflow:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/creator-cloud-studio-workflow:latest
docker tag creator-cloud-studio-data:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/creator-cloud-studio-data:latest

docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/creator-cloud-studio-presentation:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/creator-cloud-studio-workflow:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/creator-cloud-studio-data:latest
```

### 6.2 Create the SQS Queue

```bash
aws sqs create-queue --queue-name creator-cloud-studio-submission-queue
```

Save the queue URL and ARN.

### 6.3 Create the 3 Lambda Functions

Create ZIP packages from:

- `functions/submission_event/lambda_function.py`
- `functions/processing_function/lambda_function.py`
- `functions/result_update/lambda_function.py`

Example:

```bash
cd functions/submission_event
zip submission-event.zip lambda_function.py

cd ../processing_function
pip install -r requirements.txt -t .
zip -r processing.zip lambda_function.py *

cd ../result-update
pip install -r requirements.txt -t .
zip -r result-update.zip lambda_function.py *

aws lambda create-function --function-name submission-event-fn --runtime python3.11 --role <lambda-role-arn> --handler lambda_function.lambda_handler --zip-file fileb://submission-event.zip
aws lambda create-function --function-name processing-fn --runtime python3.11 --role <lambda-role-arn> --handler lambda_function.lambda_handler --zip-file fileb://processing.zip
aws lambda create-function --function-name result-update-fn --runtime python3.11 --role <lambda-role-arn> --handler lambda_function.lambda_handler --zip-file fileb://result-update.zip
```

### 6.4 Connect SQS to Submission Event Lambda

```bash
aws lambda create-event-source-mapping \
  --function-name submission-event-fn \
  --batch-size 1 \
  --event-source-arn <submission-queue-arn>
```

### 6.5 Deploy the 3 ECS Fargate Services

Deploy:

- `presentation-service` behind an internet-facing ALB
- `workflow-service` as an internal service
- `data-service` as an internal service

Required environment variables:

### Presentation Service

- `WORKFLOW_SERVICE_URL=http://<internal-workflow-service-endpoint>:5001`

### Workflow Service

- `DATA_SERVICE_URL=http://<internal-data-service-endpoint>:5002`
- `LOCAL_ASYNC_MODE=false`
- `AWS_REGION=us-east-1`
- `SUBMISSION_QUEUE_URL=<your-sqs-queue-url>`
- `PROCESSING_FUNCTION_NAME=processing-fn`
- `RESULT_UPDATE_FUNCTION_NAME=result-update-fn`

### Data Service

- No special environment variables required

## 7. Testing Method

### Browser Test

1. Open [http://localhost:5000](http://localhost:5000)
2. Submit a form
3. Wait for processing
4. Confirm that the status becomes `INCOMPLETE`, `NEEDS REVISION`, or `READY`

### API Test Example

Submit:

```bash
curl -X POST http://localhost:5001/submit \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Campus Expo\",\"description\":\"A complete poster submission for the upcoming student innovation expo event.\",\"poster_filename\":\"expo.jpeg\"}"
```

Then read:

```bash
curl http://localhost:5001/result/<submission-id>
```

## 8. Why Containers for Some Parts and Serverless for Others

### Containers

- Presentation Service needs a persistent web server for HTML pages
- Workflow Service needs a stable API endpoint for browser submissions
- Data Service needs a stable HTTP interface and persistent local database access

### Serverless

- Submission Event Function is event-triggered by SQS
- Processing Function is short, stateless, and rule-based
- Result Update Function is a small integration task triggered only when results are ready

This separation demonstrates the assignment themes clearly:

- service decomposition
- execution-model choice
- event-driven workflow
- container + serverless integration

## 9. Architecture Diagram Explanation

You can explain the architecture to your instructor like this:

- The user interacts only with the Presentation Service.
- The Presentation Service sends the form payload to the Workflow Service.
- The Workflow Service writes a `PENDING` record to the Data Service first.
- The Workflow Service emits a submission event to SQS.
- SQS triggers the Submission Event Function.
- The Submission Event Function forwards the request to the Processing Function.
- The Processing Function applies the assignment rules and generates the final status plus note.
- The Result Update Function writes the final result back into the Data Service.
- The user opens the result page and sees the updated final status.

This proves the application is not a simple synchronous monolith. It is a small but valid hybrid cloud system built around asynchronous event-driven processing.
