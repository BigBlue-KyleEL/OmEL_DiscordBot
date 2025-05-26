# 🛡️ Om’EL — The Watcher of the House of EL

Om’EL is a Discord bot designed to aid the House of EL in issuing quests, managing their fulfillment, and archiving heroic deeds — all wrapped in a lore-rich experience.

---

## ✨ Features

- 🎖️ **Quest Creation via Modal**
- 🪶 **Claiming and Sealing Quests**
- 📜 **Automatic Logging of Sealed Quests**
- 🕰️ **Time-based Shutdown Guard (Asia/Manila)**
- 🔐 **Environment-based Configuration**
- 📁 **Rotating Log Files for Historical Records**

---

## 📦 Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/omel.git
   cd omel
   ```

2. **Create a virtual environment & install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** (based on `.env.example`)
   ```env
   DISCORD_TOKEN=your-bot-token
   GUILD_ID=your-guild-id
   EDICTS_OF_EL_CHANNEL_ID=123456789012345678
   HALL_OF_DEEDS_CHANNEL_ID=123456789012345678
   OATHBOUND_SCROLLS_CHANNEL_ID=123456789012345678
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

---

## 🧠 Philosophy

Om’EL isn’t just a bot — it’s a Keeper of Oaths, a Sentinel of Scrolls, and a Chronicler of every deed in the House of EL.

---

## 📁 Folder Structure

```
.
├── bot.py
├── flavor.py
├── db.py
├── logging_config.py  # if you separated it
├── .env
├── .gitignore
├── omel.log
└── README.md
```

---

## 🛠️ Tech Stack

- Python 3.11+
- discord.py (v2.3+)
- PostgreSQL (via asyncpg or psycopg2)
- dotenv for secrets
- `pytz` + `datetime` for scheduling
- `logging` + `RotatingFileHandler` for persistent logs

---

## 🔐 Notes

- `.env` is excluded via `.gitignore`
- Bot shuts down outside allowed hours (8 AM–12 MN Manila Time)

---

## 📚 Future Plans

- 🎮 Multi-quest support
- ⏰ Scheduled reminders
- 📦 Extension modules for more lore-rich mechanics

---

## 🏛️ Credits

Crafted with honor by the House of EL 🏹  
With guidance from the Loremasters (and ChatGPT ☁️)