import os
import random
import json
from flask import Flask, jsonify
from slackclient import SlackClient

app = Flask(__name__)

filepath = '/home/scollins/PycharmProjects/meme-slack/memes.txt'
users = {}
slack_token = os.environ.get('SLACK_API_TOKEN',
                             'xoxp-165009029618-165009030770-225009348531-2a387c6033cfdc106b8e59ab88aadb3b')


def find_user(id):
    if id in users:
        return users[id]
    client = SlackClient(slack_token)
    user = client.api_call('users.info', user=id)['user']
    print(user)
    users[id] = {
        'id': user['id'],
        'name': user['real_name'],
        'avatar': user['profile']['image_512']
    }
    return users[id]


def return_message(meme):
    return jsonify({
        'time': meme['time'],
        'text': meme['text'],
        'user': find_user(meme['user']),
    })


@app.route('/')
def status():
    return 'Found meme file %s' % os.path.getsize(filepath)


@app.route('/random')
def random_message():
    with open(filepath) as file:
        meme = json.loads(random.choice(file.read().splitlines()))
    return return_message(meme)


@app.route('/latest')
def latest_message():
    with open(filepath) as file:
        meme = json.loads(file.readlines()[-1])
    return return_message(meme)


if __name__ == '__main__':
    app.run()
