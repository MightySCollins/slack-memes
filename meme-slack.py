from random import randint
import time
import sqlite3

from flask import Flask, jsonify, g, request
from slackclient import SlackClient

app = Flask(__name__)

DATABASE = '/home/scollins/PycharmProjects/meme-slack/memes.db'
TOKEN = 'xoxp-165009029618-165009030770-225009348531-2a387c6033cfdc106b8e59ab88aadb3b'


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def update_user(id):
    pass

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/random')
def random():
    total = query_db("SELECT count(*) FROM messages", one=True)
    id = randint(1, total[0])
    return jsonify(
        query_db("SELECT * FROM messages WHERE id = ?", [id], one=True))


@app.route('/latest')
def latest():
    return jsonify(
        query_db("SELECT * FROM messages ORDER BY ts DESC LIMIT 1", one=True))


@app.route('/board/random')
def random():
    total = query_db("SELECT count(*) FROM messages", one=True)
    id = randint(1, total[0])
    meme = query_db("SELECT * FROM messages WHERE id = ?", [id], one=True)
    return meme[2]


@app.route('/slack/event')
def event():
    event = request.get_json()
    if event['event']['type'] == 'message':
        message = event['event']
        query_db("INSERT INTO messages VALUES (NULL, ?, ?, ?, ?)",
                 [message['channel'], message['user'], message['text'],
                  message['ts']])
        update_user(message['user'])


@app.route('/slack/meme')
def meme():
    if request.form['token'] != 'token':
        return 'Invalid token'

    query_db("INSERT INTO messages VALUES (NULL, ?, ?, ?, ?)",
             [request.form['channel_id'], request.form['user_id'], request.form['text'],
              int(time.time())])
    return 'Your meme has been saved'


if __name__ == '__main__':
    app.run()
