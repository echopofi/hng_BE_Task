from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime, timezone

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/classify")
async def classify(name: str = Query(default=None)):
    if name is None or name.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "name query parameter is required"}
        )
    
    if not any(char.isalpha() for char in name):
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "name query parameter must be a valid string"}
        )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.genderize.io",
                params={"name": name},
                timeout=5.0
            )
            
            if response.status_code != 200:
                return JSONResponse(
                    status_code=502,
                    content={"status": "error", "message": "External API error"}
                )
                
            data = response.json()
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Internal server error"}
            )

    gender = data.get("gender")
    sample_size = data.get("count", 0)
    probability = data.get("probability", 0)

    if gender is None or sample_size == 0:
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "message": "No prediction available for the provided name"}
        )

    is_confident = (probability >= 0.7) and (sample_size >= 100)
    processed_at = datetime.now(timezone.utc).isoformat(timespec='seconds').replace("+00:00", "Z")

    return {
        "status": "success",
        "data": {
            "name": name,
            "gender": gender,
            "probability": probability,
            "sample_size": sample_size,
            "is_confident": is_confident,
            "processed_at": processed_at
        }
    }