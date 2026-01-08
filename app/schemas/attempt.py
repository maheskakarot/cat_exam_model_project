from pydantic import BaseModel
from typing import List, Union
from datetime import datetime

class AnswerPayload(BaseModel):
    question_id: str
    answer: Union[str, int, float, List[str]]

class SaveAnswersRequest(BaseModel):
    answers: List[AnswerPayload]

class StartAttemptResponse(BaseModel):
    attempt_id: str
    attempt_number: int
    started_at: datetime

class SubmitResponse(BaseModel):
    status: str
    message: str
