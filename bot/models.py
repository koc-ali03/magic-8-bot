from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserStats(Base):
    __tablename__ = 'user_stats'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String)
    message_count = Column(Integer, default=0)
    trigger_count = Column(Integer, default=0)

class ChatState(Base):
    __tablename__ = 'chat_state'

    chat_id = Column(Integer, primary_key=True)
    current_count = Column(Integer, default=0)
    target = Column(Integer)

class ChatConfig(Base):
    __tablename__ = 'chat_config'

    chat_id = Column(Integer, primary_key=True)
    min_target = Column(Integer, default=30)
    max_target = Column(Integer, default=70)
    enabled = Column(Boolean, default=True)