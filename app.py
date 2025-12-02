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
    bot.reply_to (m, "Input in format <paid | share> <amount> e.g. paid 1500 \n")

#receive imput from user
@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Expect format: "@username amount"
    try:
        kind, amount_str = message.text.split()

        username = message.from_user.username   # sender of message
        kind = kind.lower()
        amount = int(amount_str)

        ok = db.record_debt(bot, message, username, kind, amount)

        if ok:
            bot.reply_to(message, f"Recorded. \n @{username} → Balance: {net} RSD")
        else:
            bot.reply_to(message, "Not recorded (error).")
    except Exception:
        bot.reply_to(message, "Invalid format. Use: @user amount")



if __name__ == "__main__":
    app.run(debug=True)
