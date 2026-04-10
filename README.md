# Name Classification API (Stage 0)

A FastAPI-based microservice that integrates with the Genderize API to predict gender based on a name, featuring data processing and confidence logic.

## Setup Instructions
1. Clone the repo: `git clone github.com/echopofi`
2. Install dependencies: `pip install fastapi uvicorn httpx`
3. Run the server: `uvicorn main:app --reload`

## API Endpoint
- **GET** `/api/classify?name=<name>`

## Tech Stack
- Python / FastAPI
- Httpx (Async API calls)
- Render/Vercel (Deployment)