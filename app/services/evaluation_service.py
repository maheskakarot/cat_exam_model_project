from collections import defaultdict

from app.database.connection import (
    questions_collection,
    answers_collection,
    results_collection,
)
from datetime import datetime

from bson import ObjectId
from app.database.redis import redis_client
from datetime import datetime


class EvaluationService:

    @staticmethod
    async def evaluate_attempt(attempt_id: str):
        answers = await answers_collection.find(
            {"attempt_id": attempt_id}
        ).to_list(None)

        attempt = await results_collection.database.test_attempts.find_one(
            {"_id": ObjectId(attempt_id)}
        )

        user_id = attempt["user_id"]
        test_id = attempt["test_id"]

        question_ids = [a["question_id"] for a in answers]

        questions = await questions_collection.find(
            {"_id": {"$in": question_ids}}
        ).to_list(None)

        question_map = {str(q["_id"]): q for q in questions}

        total_score = 0
        subject_scores = defaultdict(float)

        for ans in answers:
            q = question_map.get(ans["question_id"])
            if not q:
                continue

            score_delta = EvaluationService._evaluate_question(q, ans["answer"])
            total_score += score_delta
            subject_scores[q["subject"]] += score_delta

        result_doc = {
            "attempt_id": attempt_id,
            "user_id": user_id,
            "test_id": test_id,
            "total_score": total_score,
            "subject_scores": dict(subject_scores),
            "evaluated_at": datetime.utcnow(),
        }

        await results_collection.insert_one(result_doc)

        # Update rankings
        EvaluationService._update_rankings(
            test_id, user_id, total_score, subject_scores
        )

    @staticmethod
    def _evaluate_question(question: dict, user_answer):
        q_type = question["type"]

        if q_type == "MCQ":
            return (
                question["marks"]
                if user_answer == question["correct_answer"]
                else -question.get("negative_marks", 0)
            )

        if q_type == "MSQ":
            if set(user_answer) == set(question["correct_answer"]):
                return question["marks"]
            return -question.get("negative_marks", 0)

        if q_type == "NUMERICAL":
            min_v = question["correct_answer"]["min"]
            max_v = question["correct_answer"]["max"]
            return (
                question["marks"]
                if min_v <= user_answer <= max_v
                else -question.get("negative_marks", 0)
            )

        return 0

    @staticmethod
    def _update_rankings(test_id, user_id, total_score, subject_scores):
        # Overall leaderboard
        redis_client.zadd(
            f"leaderboard:test:{test_id}",
            {user_id: total_score}
        )

        # Subject-wise leaderboard
        for subject, score in subject_scores.items():
            redis_client.zadd(
                f"leaderboard:test:{test_id}:subject:{subject}",
                {user_id: score}
            )

