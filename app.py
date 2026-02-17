from flask import request
import flask
from flask import Flask
from flask_sslify import SSLify
# from dotenv import load_dotenv
# load_dotenv()
import os
import db
from datetime import timezone
from zoneinfo import ZoneInfo

import telebot

db.init_db()
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), threaded=False)
BELGRADE = ZoneInfo("Europe/Belgrade")
app = Flask('__name__')
# sslify = SSLify(app)

@app.route('/', methods=['POST','GET'])
def home():
    if request.method == 'POST':
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])

        else:
            flask.abort(403)
    return 'OK'


#curl -F "url=https://nicobelic.pythonanywhere.com/" https://api.telegram.org/bot<token>/setWebhook

#process "/start" command
# @bot.message_handler(commands=['start'])
# def start(m):
#     bot.reply_to (m, "Input in format <paid | share> <amount> e.g. paid 1500 \n")


@bot.message_handler(commands=["me"])
def me_handler(message):
    if message.chat.type != "private":
        return
    username = message.from_user.username or message.from_user.first_name
    net = db.my_balance(username)

    bot.reply_to(
        message,
        f"@{username} → Your balance: {net} RSD"
    )

@bot.message_handler(commands=["all"])
def all_handler(message):
    if message.chat.type != "private":
        return
    lines = []
    for user in db.all_usernames():
        net = db.my_balance(username=user)
        sign = "+" if net > 0 else ""
        lines.append(f"@{user}: {sign}{net} RSD")

    reply_text = "<b>📊 Group balance:</b>\n" + "\n".join(lines)
    bot.reply_to(message, reply_text, parse_mode="HTML")

@bot.message_handler(commands=["history"])
def history_handler(message):
    # only private chats
    if message.chat.type != "private":
        return

    username = message.from_user.username or message.from_user.first_name

    # get all transactions with running balance
    all_rows = db.transactions_with_running_balance(username)

    if not all_rows:
        bot.reply_to(message, "No transactions found.")
        return

    last_10 = all_rows[-10:]  # last 10 oldest->newest

    # Format a padded table
    lines = []

    # column widths
    w_date = 10
    w_user = 12
    w_amount = 7
    w_with = 12
    w_bal = 8

    # optional header
    header = (
        "DATE".ljust(w_date) + " | "
        + "USER".ljust(w_user) + " | "
        + "AMOUNT".center(w_amount) + " | "
        + "WITH".ljust(w_with) + " | "
        + "BAL".rjust(w_bal)
    )
    lines.append(header)
    lines.append("-" * len(header))

    for r, balance in last_10:
        # local date
        if r.created_at:
            local_dt = r.created_at.astimezone(BELGRADE)
            date_str = local_dt.strftime("%d/%m/%y")
        else:
            date_str = "NULL"

        # padded fields
        date_col = date_str.ljust(w_date)
        user_col = f"@{r.username}".ljust(w_user)

        sign = "+" if r.kind == "paid" else "-"
        amt_col = f"{sign}{r.amount_din}".rjust(w_amount)

        cp_col = (f"@{r.counterparty}" if r.counterparty else "NULL").ljust(w_with)
        bal_col = f"{balance}".rjust(w_bal)

        line = (
            f"{date_col} | {user_col} | {amt_col} | {cp_col} | {bal_col}"
        )
        lines.append(line)

    # build final message with monospace code block
    msg = "/history\n\n```\n" + "\n".join(lines) + "\n```"
    bot.reply_to(message, msg, parse_mode="Markdown")

#receive input from user
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.chat.type == "private":
        return

    if not message.text.startswith("/"):
        return

    if message.text.startswith(("/me", "/all", "/start")):
        return

    try:
        kind, amount_str, creditor = message.text[1:].split()

        debtor = message.from_user.username or message.from_user.first_name   # sender of a message
        kind = kind.lower()
        creditor = creditor.lstrip("@")

        if kind not in ("paid", "share"):
            bot.reply_to(message, "Unknown command. Use /paid or /share.")
            return

        amount = int(amount_str)

        self = db.record_debt(debtor, kind, amount, counterparty=creditor)

        if kind == "paid":
            other = db.record_debt(creditor, "share", amount, counterparty=debtor)
        if kind == "share":
            other = db.record_debt(creditor, "paid", amount, counterparty=debtor)

        if self and other:
            net_debtor = db.my_balance(debtor)
            net_creditor = db.my_balance(creditor)
            bot.reply_to(message, f"Recorded. \n @{debtor} → Balance: {net_debtor} RSD \n @{creditor} → Balance: {net_creditor} RSD")
        else:
            bot.reply_to(message, "Not recorded (error).")
    except Exception:
        bot.reply_to(message, "Invalid format. Use: /paid | /share <amount> @creditor_username")

if __name__ == "__main__":
    app.run(debug=True)
    # bot.remove_webhook()
    # bot.polling()