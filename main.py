from fastapi import FastAPI, Query, HTTPException
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

@app.get("/")
def root():
    return {"status": "server is running"}

@app.get("/api/classify")
async def classify(name: str = Query(default=None)):

    if name is None or name.strip() == "":
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "name query parameter is required"
            }
        )
    
    if not any(char.isalpha() for char in name):
        raise HTTPException(
            status_code=422,
            detail={
                "status": "error",
                "message": "name query parameter must be a valid string"
            }
        )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://api.genderize.io",
                params={"name": name}
            )
            genderize_data = response.json()

        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "error",
                    "message": "Failed to reach Genderize API"
                }
            )
    
    
    if genderize_data.get("gender") is None or genderize_data.get("count") == 0:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "No gender data found for the provided name"
                })
    
    gender = genderize_data.get("gender")
    probability = genderize_data.get("probability")
    sample_size = genderize_data.get("count")

    is_confident = probability >= 0.7 and sample_size >= 100

    processed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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


    

