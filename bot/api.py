from fastapi import APIRouter
from .db import SessionLocal
from .models import UserStats, ChatState
from sqlalchemy import func

api_router = APIRouter(prefix="/api", tags=["api"])

@api_router.get("/group/{chat_id}/leaderboard")
def group_leaderboard(chat_id: int):
    session = SessionLocal()
    try:
        top_users = session.query(UserStats)\
            .filter_by(chat_id=chat_id)\
            .order_by(UserStats.trigger_count.desc())\
            .limit(10)\
            .all()
        
        return [
            {
                "user_id": u.user_id,
                "username": u.username,
                "trigger_count": u.trigger_count,
                "message_count": u.message_count
            }
            for u in top_users
        ]
    finally:
        session.close()

@api_router.get("/group/{chat_id}/stats")
def group_stats(chat_id: int):
    session = SessionLocal()
    try:
        total_messages = session.query(func.sum(UserStats.message_count))\
            .filter_by(chat_id=chat_id)\
            .scalar() or 0
        
        total_triggers = session.query(func.sum(UserStats.trigger_count))\
            .filter_by(chat_id=chat_id)\
            .scalar() or 0

        return {
            "chat_id": chat_id,
            "total_messages": total_messages,
            "total_triggers": total_triggers
        }
    finally:
        session.close()
