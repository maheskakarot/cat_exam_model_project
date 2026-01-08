from app.database.redis import redis_client


class RankingService:
    """
    Responsible ONLY for reading ranking data from Redis
    and calculating rank + percentile.
    """

    @staticmethod
    def _get_rank_and_percentile(redis_key: str, user_id: str):
        """
        Returns (rank, percentile) for a user from a Redis ZSET
        """
        rank = redis_client.zrevrank(redis_key, user_id)

        if rank is None:
            return None, None

        total_users = redis_client.zcard(redis_key)

        # Redis rank is 0-based
        rank = rank + 1

        percentile = round(
            ((total_users - rank) / total_users) * 100,
            2
        )

        return rank, percentile

    @staticmethod
    def get_overall_rank(test_id: str, user_id: str):
        redis_key = f"leaderboard:test:{test_id}"
        return RankingService._get_rank_and_percentile(redis_key, user_id)

    @staticmethod
    def get_subject_rank(test_id: str, subject: str, user_id: str):
        redis_key = f"leaderboard:test:{test_id}:subject:{subject}"
        return RankingService._get_rank_and_percentile(redis_key, user_id)
