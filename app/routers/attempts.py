from fastapi import APIRouter
from app.services.attempt_service import AttemptService
from app.schemas.attempt import SaveAnswersRequest

router = APIRouter(prefix="/attempts", tags=["Attempts"])

@router.post("/start/{test_id}")
async def start_attempt(test_id: str, user_id: str):
    return await AttemptService.start_attempt(user_id, test_id)

@router.post("/{attempt_id}/answers")
async def save_answers(attempt_id: str, payload: SaveAnswersRequest):
    return await AttemptService.save_answers(
        attempt_id,
        [a.dict() for a in payload.answers],
    )

@router.post("/{attempt_id}/submit")
async def submit_attempt(attempt_id: str):
    return await AttemptService.submit_attempt(attempt_id)
