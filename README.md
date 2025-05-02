# 🎱 Magic8Bot — Telegram Group Game Bot

A fun, interactive Telegram bot built with Python, FastAPI, and SQLAlchemy. Magic8Bot secretly counts group chat messages until a randomly chosen number is reached — then replies to that message with a Magic 8-Ball–style response

The bot includes:
- Persistent storage with SQLite (through SQLAlchemy)
- User stats and leaderboards
- Full webhook-based backend with FastAPI

---

## 🚀 Features

✅ Secret message counting in group chats  
✅ Magic 8-Ball reply when count hits hidden target  
✅ Fully persistent state with per-chat message tracking  
✅ Multi-group support  
✅ Admin-only command enforcement  
✅ Webhook-safe on restarts (no spam from backlog)  
✅ `.env` config with secret tokens and base URL (example file included)  

Slash commands:
- `/mystats` – View your stats in the chat
- `/leaderboard` – Top 5 most frequent triggerers
- `/ask <question>` – Ask the Magic 8-Ball directly 🎱
- `/setrange <min> <max>` – Admins set target range
- `/reset` – Admins reset the counter & choose a new target
- `/disable` / `/enable` – Admins toggle bot behavior per group  

---

## 📡 API Endpoints

These can be used to query group-specific data:

- `/api/group/<chat_id>/leaderboard` – Top users by trigger count
- `/api/group/<chat_id>/stats` – Total messages and triggers in group

Only works for groups where the bot is present.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI** – Webhook server
- **python-telegram-bot v20+**
- **SQLAlchemy** – ORM
- **SQLite**
- **dotenv** – Secret config management

---

## 📜 License
MIT License — free for personal or educational use.