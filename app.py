from flask import request
import flask
from flask import Flask
from flask_sslify import SSLify
import os
import db

import telebot


bot = telebot.TeleBot(os.environ["BOT_TOKEN"], threaded=False)

app = Flask('__name__')
sslify = SSLify(app)

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
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to (m, "Enter debt in format: <@telegram-nickname of whom you own> <debt in RSD>. E.g. @homer 500 \n")

#receive imput from user
@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Expect format: "@username amount"
    try:
        nickname, amount_str = message.text.split()
        if not nickname.startswith("@"):
            bot.reply_to(message, "Format: @user amount")
            return

        creditor = nickname[1:]               # remove '@'
        username = message.from_user.username   # sender of message
        amount = int(amount_str)
        msg_id = message.message_id

        if creditor == debtor:
            bot.reply_to(message, "You cannot owe yourself.")
            return

        ok = db.record_debt(bot, message, username, debtor, amount, msg_id)

        if ok:
            bot.reply_to(message, f"Recorded: @{debtor} → @{creditor} : {amount} RSD")
        else:
            bot.reply_to(message, "Not recorded (maybe duplicate message or error).")
        except Exception:
            bot.reply_to(message, "Invalid format. Use: @user amount")



if __name__ == "__main__":
    app.run(debug=True)
