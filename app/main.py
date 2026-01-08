from fastapi import FastAPI
from app.routers import attempts

app = FastAPI(
    title="UPSC Test Platform",
    version="1.0.0",
)

app.include_router(attempts.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
