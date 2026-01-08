from app.database.connection import (
    questions_collection,
    answers_collection,
    results_collection,
)
from datetime import datetime

class EvaluationService:

    @staticmethod
    async def evaluate_attempt(attempt_id: str):
        answers = await answers_collection.find(
            {"attempt_id": attempt_id}
        ).to_list(None)

        question_ids = [a["question_id"] for a in answers]

        questions = await questions_collection.find(
            {"_id": {"$in": question_ids}}
        ).to_list(None)

        question_map = {str(q["_id"]): q for q in questions}

        score = 0
        correct = wrong = 0

        for ans in answers:
            q = question_map.get(ans["question_id"])
            if not q:
                continue

            if EvaluationService._is_correct(q, ans["answer"]):
                score += q["marks"]
                correct += 1
            else:
                score -= q.get("negative_marks", 0)
                wrong += 1

        result_doc = {
            "attempt_id": attempt_id,
            "score": score,
            "correct": correct,
            "wrong": wrong,
            "evaluated_at": datetime.utcnow(),
        }

        await results_collection.insert_one(result_doc)

    @staticmethod
    def _is_correct(question: dict, user_answer):
        q_type = question["type"]

        if q_type == "MCQ":
            return user_answer == question["correct_answer"]

        if q_type == "MSQ":
            return set(user_answer) == set(question["correct_answer"])

        if q_type == "NUMERICAL":
            return (
                question["correct_answer"]["min"]
                <= user_answer
                <= question["correct_answer"]["max"]
            )

        return False
