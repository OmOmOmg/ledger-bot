from flask import request
import flask
from flask import Flask
from flask_sslify import SSLify
import os
import db

import telebot

db.init_db()
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), threaded=False)

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


#curl -F "url=https://nckkk.pythonanywhere.com/" https://api.telegram.org/bot<token>/setWebhook

#process "/start" command
# @bot.message_handler(commands=['start'])
# def start(m):
#     bot.reply_to (m, "Input in format <paid | share> <amount> e.g. paid 1500 \n")


@bot.message_handler(commands=["me"])
def me_handler(message):
    username = message.from_user.username
    net = db.my_balance(username)

    bot.reply_to(
        message,
        f"@{username} → Your balance: {net} RSD"
    )

@bot.message_handler(commands=["all"])
def all_handler(message):
    lines = []
    for user in db.all_usernames():
        net = db.my_balance(username=user)
        sign = "+" if net > 0 else ""
        lines.append(f"@{user}: {sign}{net} RSD")

    reply_text = "<b>📊 Group balance:</b>\n" + "\n".join(lines)
    bot.reply_to(message, reply_text, parse_mode="HTML")

#receive imput from user
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.chat.type == "private":
        return

    if not message.text.startswith("/"):
        return

    if message.text.startswith(("/me", "/all", "/start")):
        return

    try:
        kind, amount_str = message.text[1:].split()

        username = message.from_user.username   # sender of message
        kind = kind.lower()

        if kind not in ("paid", "share"):
            bot.reply_to(message, "Unknown command. Use /paid or /share.")
            return

        amount = int(amount_str)

        ok = db.record_debt(username, kind, amount)

        if ok:
            net = db.my_balance(username)
            bot.reply_to(message, f"Recorded. \n @{username} → Balance: {net} RSD")
        else:
            bot.reply_to(message, "Not recorded (error).")
    except Exception:
        bot.reply_to(message, "Invalid format. Use: /paid <amount> or /share <amount>")

if __name__ == "__main__":
    app.run(debug=True)