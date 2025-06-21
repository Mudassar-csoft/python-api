from fastapi import Header, HTTPException, status

API_KEY = "Pk.Privacy01"  # Or load via os.getenv("API_KEY")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
