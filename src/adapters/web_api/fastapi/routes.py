from fastapi import APIRouter

test_router = APIRouter()

@test_router.get("/health")
async def health_check():
    return {"status": "healthy"}