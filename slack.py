import os
import time
import logging
import sys
import json
from slackclient import SlackClient

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class SlackWatcher:
    CHANNEL = 'testing-memes'
    FILE = 'memes.txt'
    last_message = ''
    users = {}

    def default(self, event):
        logging.debug('Unhandled message type %s' % event['type'])

    def message(self, event):
        if event['channel'] != self.channel_id:
            logging.debug('Received unrelated message | %s' % event)
            return
        logging.info('Received possible meme | %s' % event)

        if self.last_message == event['text']:
            logging.debug('Duplicate message detected %s' % self.last_message)
            return

        with open(self.FILE, 'a') as messages:
            messages.write("%s\n" % json.dumps({
                'time': event['ts'],
                'text': event['text'],
                'user': event['user']
            }))
        self.last_message = event['text']
        logging.info('Writing meme "%s" to file' % event['text'])

    def __init__(self, token):
        self.client = SlackClient(token)
        self.channel_id = self.get_channel_id(self.CHANNEL)

        try:
            with open(self.FILE) as file:
                self.last_message = json.loads(file.readlines()[-1])['text']
            logging.debug('Found last message %s' % self.last_message)
        except (IndexError, FileNotFoundError):
            logging.info('Unable to get last message')

    def get_channel_id(self, name):
        channels = self.client.api_call(
            'channels.list',
            exclude_archived=1
        )
        for channel in channels['channels']:
            logging.debug('Found channel %s | %s' % (channel['name'], channel))
            if channel['name'] == name:
                logging.info(
                    'Found id %s for channel %s' % (channel['id'], name))
                return channel['id']

    def process_event(self, event):
        if event['type'] == 'message':
            return self.message(event)
        return self.default(event)

    def watch(self):
        if self.client.rtm_connect():
            while True:
                for message in self.client.rtm_read():
                    self.process_event(message)
                time.sleep(1)
        else:
            logging.error('Connection Failed, invalid token?')


slack_token = os.environ.get('SLACK_API_TOKEN',
                             'xoxp-165009029618-165009030770-225009348531-2a387c6033cfdc106b8e59ab88aadb3b')
slack = SlackWatcher(slack_token)
slack.watch()
