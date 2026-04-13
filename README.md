
# 🍻 Telegram Debt Tracker Bot

A lightweight Telegram bot for tracking shared expenses in a group of friends.

Instead of tracking who owes whom, the bot maintains a **pool-based balance**:
- Positive → the group owes you
- Negative → you owe the group

---

## ✨ Features

- Log expenses directly in group chat
- Supports Russian-style commands:
  - `/плачу <amount> @user` — you paid for someone
  - `/торчу <amount> @user` — you owe someone
- View personal balance: `/me`
- View group balances: `/all`
- View last transactions: `/history`

---

## 🧠 How It Works

Each transaction is stored as a simple entry:

- `paid` → adds to your balance  
- `share` → subtracts from your balance  

Balance formula:
```

balance = sum(paid) - sum(share)

````

The bot records **two entries per interaction** (for both users) to keep balances consistent.

---

## ⚙️ Setup & Deployment

### 1. Clone the project

```bash
git clone <your-repo>
cd <your-project>
````

---

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

### 3. Environment variables

Create a `.env` file:

```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=sqlite:///db.sqlite3
```

---

### 4. Run locally (for testing)

```bash
python app.py
```

---

### 5. Deploy on PythonAnywhere

1. Upload project files
2. Configure WSGI file:

   * Point to your project folder
   * Ensure `.env` is loaded
   * Import Flask app:

```python
from flask_telebot import app as application
```

Reference: 

3. Set webhook:

```bash
curl -F "url=https://<your-domain>/" \
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook
```

---

## 💬 Usage

### In group chat:

```
/плачу 1500 @alice
```

→ You paid 1500 for Alice

```
/торчу 500 @bob
```

→ You owe Bob 500

---

### In private chat with bot:

* `/me` → your balance
* `/all` → all balances
* `/history` → last transactions

---



