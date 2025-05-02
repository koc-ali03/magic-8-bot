from telegram import Update
from telegram.ext import ContextTypes
from .db import SessionLocal
from .models import UserStats, ChatState, ChatConfig
from random import choice
import logging

logger = logging.getLogger(__name__)

MIN_TARGET = 30
MAX_TARGET = 70

RESPONSE = [
    "Yes.", "No.", "I guess so.",
    "Definitely!", "I doubt it.", "Probably.",
    "In your dreams.", "Absolutely not.",
    "Not even in your dreams.", "Perchance.", # inside joke
]

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

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if update.message.chat.type == "private": # If it's a direct message, the user is pretty much an admin
        return True
    member = await context.bot.get_chat_member(update.message.chat.id, update.message.from_user.id)
    return member.status in ["administrator", "creator"]

async def setrange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You must be an admin to do this.")
        return

    if len(context.args) != 2 or not all(arg.isdigit() for arg in context.args):
        await update.message.reply_text("Usage: /setrange <min> <max>")
        return

    min_target, max_target = map(int, context.args)

    if min_target > max_target:
        await update.message.reply_text("Minimum cannot be bigger than maximum.")
        return

    chat_id = update.message.chat.id

    session = SessionLocal()
    try:
        config = session.query(ChatConfig).filter_by(chat_id=chat_id).first()
        if not config:
            config = ChatConfig(chat_id=chat_id)

        config.min_target = min_target
        config.max_target = max_target
        session.add(config)
        session.commit()

        await update.message.reply_text(f"Target range set to {min_target}-{max_target} (effective next round)")
    finally:
        session.close()

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You must be an admin to do this.")
        return

    session = SessionLocal()
    try:
        chat_id = update.message.chat.id
        chat_state = session.query(ChatState).filter_by(chat_id=chat_id).first()
        config = session.query(ChatConfig).filter_by(chat_id=chat_id).first()
        min_target = config.min_target if config else MIN_TARGET
        max_target = config.max_target if config else MAX_TARGET

        if not chat_state:
            chat_state = ChatState(chat_id=chat_id)

        chat_state.current_count = 0
        from random import randint
        chat_state.target = randint(min_target, max_target)
        session.add(chat_state)
        session.commit()

        await update.message.reply_text("Bot state reset and new target chosen.")
    finally:
        session.close()

async def disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You must be an admin to do this.")
        return

    session = SessionLocal()
    try:
        chat_id = update.message.chat.id
        config = session.query(ChatConfig).filter_by(chat_id=chat_id).first()
        if not config:
            config = ChatConfig(chat_id=chat_id)
        config.enabled = False
        session.add(config)
        session.commit()
        await update.message.reply_text("Bot is now disabled.")
    finally:
        session.close()

async def enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You must be an admin to do this.")
        return

    session = SessionLocal()
    try:
        chat_id = update.message.chat.id
        config = session.query(ChatConfig).filter_by(chat_id=chat_id).first()
        if not config:
            config = ChatConfig(chat_id=chat_id)
        config.enabled = True
        session.add(config)
        session.commit()
        await update.message.reply_text("Bot is now enabled.")
    finally:
        session.close()

async def eightball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text(choice(RESPONSE))

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

    config = session.query(ChatConfig).filter_by(chat_id=chat_id).first()
    if config and not config.enabled:
        return

    min_target = config.min_target if config else MIN_TARGET
    max_target = config.max_target if config else MAX_TARGET

    try:
        # Get or create ChatState for this chat
        chat_state = session.query(ChatState).filter_by(chat_id=chat_id).first()
        if not chat_state:
            from random import randint
            chat_state = ChatState(chat_id=chat_id, current_count=0, target=randint(min_target, max_target))
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
            await update.message.reply_text(choice(RESPONSE), reply_to_message_id=update.message.message_id)

            # Increment user's trigger_count
            user_stats.trigger_count += 1

            # Reset chat counter and pick a new target
            chat_state.current_count = 0
            from random import randint
            chat_state.target = randint(min_target, max_target)

            session.commit()
    except Exception as e:
        logger.exception("DB ERROR:")
    finally:
        session.close()