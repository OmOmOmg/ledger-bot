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

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])

        else:
            flask.abort(403)
    return 'OK'


# curl -F "url=https://nicobelic.pythonanywhere.com/" https://api.telegram.org/bot<token>/setWebhook

# process "/start" command
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
    if message.chat.type != "private":
        return

    username = message.from_user.username or message.from_user.first_name

    all_rows = db.transactions_with_running_balance(username)

    if not all_rows:
        bot.reply_to(message, "No transactions found.")
        return

    last_10 = all_rows[-10:]

    lines = []

    for r, balance in last_10:
        if r.created_at:
            local_dt = r.created_at.astimezone(BELGRADE)
            date_str = local_dt.strftime("%d/%m/%y")
        else:
            date_str = "NULL"

        sign = "+" if r.kind == "paid" else "-"
        counterparty = f"@{r.counterparty}" if r.counterparty else "NULL"

        lines.append(f"@{r.username} {sign}{r.amount_din} {counterparty}")
        lines.append(f"Date: {date_str}")
        lines.append(f"Balance: {balance}")
        lines.append("")  # spacing between entries

    msg = "\n".join(lines)
    bot.reply_to(message, msg)


# receive input from user
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

        debtor = message.from_user.username or message.from_user.first_name  # sender of a message
        kind_rus = kind.lower()
        creditor = creditor.lstrip("@")

        if kind_rus not in ("плачу", "торчу"):
            bot.reply_to(message, "Unknown command. Use /плачу or /торчу.")
            return
        if kind_rus == "плачу":
            kind = "paid"
        elif kind_rus == "торчу":
            kind = "share"

        amount = int(amount_str)

        status = db.record_transfer(
            debtor=debtor,
            kind=kind,
            amount_din=amount,
            creditor=creditor,
            message_id=message.message_id,
        )

        if status == "created":
            net_debtor = db.my_balance(debtor)
            net_creditor = db.my_balance(creditor)
            bot.reply_to(message,
                         f"Recorded. \n @{debtor} → Balance: {net_debtor} RSD \n @{creditor} → Balance: {net_creditor} RSD")
        elif status == "duplicate":
            return
        else:
            bot.reply_to(message, "Not recorded (error).")

    except Exception:
        bot.reply_to(message, "Invalid format. Use: /плачу | /торчу <amount> @creditor_username")


if __name__ == "__main__":
    app.run(debug=True)
    # bot.remove_webhook()
    # bot.polling()
