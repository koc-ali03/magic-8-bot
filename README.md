# 🎱 Magic8Bot — Telegram Group Game Bot

A fun, interactive Telegram bot built with Python, FastAPI, and SQLAlchemy. Magic8Bot secretly counts group chat messages until a randomly chosen number is reached — then replies to that message with a Magic 8-Ball–style response

The bot includes:
- Persistent storage with SQLite (through SQLAlchemy)
- User stats and leaderboards
- Full webhook-based backend with FastAPI

---

## 🚀 Features

- ✅ Message counting in Telegram group chats  
- ✅ Random target triggering & reset  
- ✅ Magic 8-Ball replies  
- ✅ Persistent stats per user & chat  
- ✅ Slash commands:
  - `/mystats` – view your stats
  - `/leaderboard` – see top 8-ball triggers

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