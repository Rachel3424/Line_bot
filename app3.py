from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import json
import configparser
import openai
from openai import OpenAI


# Setup
config = configparser.ConfigParser()
config.read('config.ini')

# OpenAI model
def legal_text(user_text):
    try:
        client = OpenAI(organization=config.get('OpenAI','organization'),
                        api_key=config.get('OpenAI','api_key'))
        response = client.chat.completions.create(
        model=config.get('OpenAI','model'),
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_text}
        ]
    )
        answer = (response.choices[0].message.content)
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
            reply = ':)>'

        print(reply)
        line_bot_api.reply_message(tk, TextSendMessage(reply))
    except:
        print(body)
    return 'OK'

if __name__ == "__main__":
    app.run(port=9988)
