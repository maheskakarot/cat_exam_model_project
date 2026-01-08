from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

# Collections
users_collection = db.users
tests_collection = db.tests
questions_collection = db.questions
attempts_collection = db.test_attempts
answers_collection = db.answers
results_collection = db.evaluation_results
