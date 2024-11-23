from langchain_community.chat_message_histories import RedisChatMessageHistory
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

def create_session_id():
    return str(uuid.uuid4())

def get_history(session_id):
    history = RedisChatMessageHistory(session_id, url=os.environ.get("REDIS_URL"))
    return history

def clear_history(session_id):
    history = RedisChatMessageHistory(session_id, url=os.environ.get("REDIS_URL"))
    history.clear()
    return "Session cleared"