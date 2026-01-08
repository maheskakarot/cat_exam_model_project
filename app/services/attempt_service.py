from datetime import datetime
from bson import ObjectId
from app.database.connection import attempts_collection
from app.services.evaluation_service import EvaluationService
from app.database.connection import answers_collection


class AttemptService:

    @staticmethod
    async def start_attempt(user_id: str, test_id: str):
        # Count previous attempts
        attempt_count = await attempts_collection.count_documents(
            {"user_id": user_id, "test_id": test_id}
        )

        attempt_doc = {
            "user_id": user_id,
            "test_id": test_id,
            "attempt_number": attempt_count + 1,
            "status": "IN_PROGRESS",
            "started_at": datetime.utcnow(),
            "submitted_at": None,
        }

        result = await attempts_collection.insert_one(attempt_doc)

        return {
            "attempt_id": str(result.inserted_id),
            "attempt_number": attempt_doc["attempt_number"],
            "started_at": attempt_doc["started_at"],
        }



    @staticmethod
    async def save_answers(attempt_id: str, answers: list):
        operations = []

        for ans in answers:
            operations.append(
                answers_collection.update_one(
                    {
                        "attempt_id": attempt_id,
                        "question_id": ans["question_id"],
                    },
                    {
                        "$set": {
                            "answer": ans["answer"],
                            "updated_at": datetime.utcnow(),
                        }
                    },
                    upsert=True,
                )
            )

        # Execute sequentially (can be optimized later)
        for op in operations:
            await op

        return {"status": "saved"}



    @staticmethod
    async def submit_attempt(attempt_id: str):
        attempt = await attempts_collection.find_one(
            {"_id": ObjectId(attempt_id)}
        )

        if not attempt:
            raise ValueError("Attempt not found")

        if attempt["status"] != "IN_PROGRESS":
            return {"status": "already_submitted"}

        await attempts_collection.update_one(
            {"_id": ObjectId(attempt_id)},
            {
                "$set": {
                    "status": "SUBMITTED",
                    "submitted_at": datetime.utcnow(),
                }
            },
        )

        # Evaluate immediately (later async)
        await EvaluationService.evaluate_attempt(attempt_id)

        return {
            "status": "submitted",
            "message": "Evaluation completed",
        }

