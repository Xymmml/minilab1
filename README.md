# Creator Cloud Studio - Poster Submission System

## Project Overview

This is a cloud-native application for handling event poster submissions, built using a hybrid architecture combining container-based services and serverless functions.

## Architecture

### 6 Required Components

| Component | Type | Role |
|-----------|------|------|
| Presentation Service | Container | Accept user submissions and display results |
| Workflow Service | Container | Create submission records and trigger processing |
| Data Service | Container | Store and retrieve submission records |
| Submission Event Function | Serverless | Convert submission events to processing requests |
| Processing Function | Serverless | Apply validation rules and compute results |
| Result Update Function | Serverless | Update stored records with computed results |

## Workflow

```
User submits form → Presentation Service → Workflow Service → Data Service (create record)
→ Submission Event Function → Processing Function → Result Update Function
→ Data Service (update record) → User views result
```

## Processing Rules

1. **INCOMPLETE**: Any required field is missing (title, description, or poster filename)
2. **NEEDS REVISION**: All fields present, but:
   - Description is less than 30 characters, OR
   - Poster filename doesn't end with .jpg/.jpeg/.png
3. **READY**: All validations pass

## Running the Application

### Start all services:
```bash
docker-compose up
```

Or run locally without Docker:
```bash
pip install flask flask-cors
python containers/data_service/app.py &
python containers/workflow_service/app.py &
python containers/presentation_service/app.py &
```

## API Endpoints

- `POST /submit` - Submit a new poster
- `GET /submissions/<id>` - View submission status
- `GET /health` - Health check endpoint
