# coding: UTF-8
import requests
import json

import env.local as CONFIG

def post_slack(text, channel = "random"):
    requests.post(CONFIG.INCOMING_WEBHOOK_URL, data=json.dumps({
        'text': text,  # 投稿内容
        "channel": channel,  # channel
        'link_names': 1,  # 名前をリンク化
    }))


if __name__ == '__main__':
    post_message = "test"
    post_slack(post_message)
