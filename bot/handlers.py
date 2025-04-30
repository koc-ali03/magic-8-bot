from telegram import Update
from telegram.ext import ContextTypes
from .db import SessionLocal
from .models import UserStats, ChatState
import logging

logger = logging.getLogger(__name__)

MIN_TARGET = 30
MAX_TARGET = 70

async def mystats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.chat:
        return

    session = SessionLocal()

    chat_id = update.message.chat.id
    user_id = update.message.from_user.id

    try:
        user_stats = session.query(UserStats).filter_by(chat_id=chat_id, user_id=user_id).first()

        if not user_stats:
            await update.message.reply_text("You have no stats yet.")
        else:
            await update.message.reply_text(
                f"Stats for {update.message.from_user.first_name}:\n"
                f"Messages Sent: {user_stats.message_count}\n"
                f"8-Ball Triggers: {user_stats.trigger_count}"
            )
    finally:
        session.close()

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.chat:
        return

    session = SessionLocal()

    chat_id = update.message.chat.id

    try:
        top_users = session.query(UserStats)\
            .filter_by(chat_id=chat_id)\
            .order_by(UserStats.trigger_count.desc())\
            .limit(5)\
            .all()

        if not top_users:
            await update.message.reply_text("No leaderboard yet.")
            return

        text = "Top 5 Users:\n"
        for i, user in enumerate(top_users, 1):
            name = user.username or f"User {user.user_id}"
            text += f"{i}. {name}: {user.trigger_count} triggers\n"

        await update.message.reply_text(text)
    finally:
        session.close()

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.chat:
        return
    
    logger.info(f"[MSG] Received message from {update.message.from_user.id} in chat {update.message.chat.id}")

    session = SessionLocal()

    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    if not username:
        username = update.message.from_user.full_name


    try:
        # Get or create ChatState for this chat
        chat_state = session.query(ChatState).filter_by(chat_id=chat_id).first()
        if not chat_state:
            from random import randint
            chat_state = ChatState(chat_id=chat_id, current_count=0, target=randint(MIN_TARGET, MAX_TARGET))
            session.add(chat_state)
            session.commit()

        # Increment current message count
        chat_state.current_count += 1
        session.commit()

        # Get or create UserStats for this user in this chat
        user_stats = session.query(UserStats).filter_by(chat_id=chat_id, user_id=user_id).first()
        if not user_stats:
            user_stats = UserStats(chat_id=chat_id, user_id=user_id, username=username)
            session.add(user_stats)
            session.commit()
        
        if user_stats.username != username:
            user_stats.username = username

        user_stats.message_count += 1
        session.commit()

        logger.info(f"Current count: {chat_state.current_count}, Target: {chat_state.target}")

        # Check if we've reached the magic number
        if chat_state.current_count >= chat_state.target:
            from random import choice
            response = choice([
                "Yes.", "No.", "I guess so.",
                "Definitely!", "I doubt it.", "Probably.",
                "In your dreams.", "Absolutely not.",
                "Not even in your dreams."
            ])

            await update.message.reply_text(response, reply_to_message_id=update.message.message_id)

            # Increment user's trigger_count
            user_stats.trigger_count += 1

            # Reset chat counter and pick a new target
            chat_state.current_count = 0
            from random import randint
            chat_state.target = randint(MIN_TARGET, MAX_TARGET)

            session.commit()
    except Exception as e:
        logger.exception("DB ERROR:")
    finally:
        session.close()