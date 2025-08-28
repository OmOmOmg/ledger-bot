from flask import Flask
from flask import request
from flask_sslify import SSLify
import flask

import requests
import json
import telebot

bot = telebot.TeleBot("$token", threaded=False)

app = Flask('__name__')
sslify = SSLify(app)

@app.route('/', methods=['POST','GET'])
def home():
    if request.method == 'POST':
        logger.info("POST incoming")
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
    bot.reply_to (m, "Enter debt in a format: @telegram-nickname <debt in RSD>. E.g. @homer 500 \n")

#receive imput from user
@bot.message_handler(content_types=["text"])
def handle_text(message):




if __name__ == "__main__":
    app.run(debug=True)
