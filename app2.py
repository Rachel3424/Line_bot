from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import json
import configparser
import google.generativeai as genai

# Setup
config = configparser.ConfigParser()
config.read('config.ini')

# Gemini api key
genai.configure(api_key=config.get('google-legal', 'api_key'))

# Pretty print
def pretty_print_format(text):
    return text

# Gemini model
def legal_text(user_text):
    model = genai.GenerativeModel('gemini-pro')

    try:
        response = model.generate_content(["tell me knowledge of the law（回覆請給我繁體中文）", user_text], stream=True)
        response.resolve()
        answer = pretty_print_format(response.text)
    except:
        answer = 'model no response!!'
    
    return answer

# Flask
app = Flask(__name__)

@app.route("/", methods=['POST']) 
def linebot():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        access_token = config.get('line-bot', 'channel_access_token')
        secret = config.get('line-bot', 'channel_secret')
        line_bot_api = LineBotApi(access_token)
        handler = WebhookHandler(secret)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        type = json_data['events'][0]['message']['type']
        # 判斷如果是文字
        if type == 'text':
            msg = json_data['events'][0]['message']['text']
            reply = legal_text(msg)

        elif type == 'image':
            reply = '可以文字詢問我法律問題喔~'

        else:
            reply = ':)'

        print(reply)
        line_bot_api.reply_message(tk, TextSendMessage(reply))
    except:
        print(body)
    return 'OK'

if __name__ == "__main__":
    app.run(port=9988)
