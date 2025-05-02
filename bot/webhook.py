from fastapi import FastAPI, Request, Header, HTTPException
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from .handlers import mystats, leaderboard, setrange, reset, disable, enable, eightball, message_handler
from .config import BOT_TOKEN, WEBHOOK_SECRET_TOKEN, BASE_URL
from .db import init_db
from .api import api_router
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(api_router)

telegram_app = Application.builder().token(BOT_TOKEN).build()

telegram_app.add_handler(CommandHandler("mystats", mystats))
telegram_app.add_handler(CommandHandler("leaderboard", leaderboard))
telegram_app.add_handler(CommandHandler("setrange", setrange))
telegram_app.add_handler(CommandHandler("reset", reset))
telegram_app.add_handler(CommandHandler("disable", disable))
telegram_app.add_handler(CommandHandler("enable", enable))
telegram_app.add_handler(CommandHandler("8ball", eightball))
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

@app.on_event("startup")
async def on_startup():
    init_db()
    await telegram_app.initialize()
    webhook_url = f"{BASE_URL}/webhook"
    await telegram_app.bot.set_webhook(url=webhook_url, secret_token=WEBHOOK_SECRET_TOKEN, drop_pending_updates=True)
    logger.info(f"Webhook set to {webhook_url}")

@app.post("/webhook")
async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: str = Header(None)):
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid secret token")
    
    update_data = await request.json()
    update = Update.de_json(update_data, telegram_app.bot)
    
    await telegram_app.process_update(update)
    
    return {"status": "ok"}
