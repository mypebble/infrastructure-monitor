#!/usr/bin/env python
"""This file handles the communication to Slack.

Sends a message to Slack using the chat.postMessage API call.
"""

from slacker import Slacker


class Slack:
    def __init__(self, config):
        self.slack_api_token = config['slack_api_token']
        self.slack_username = config['slack_username']
        self.slack_channel = config['slack_channel']
        self.slack_emote = config['slack_emote']
        self.slack_shoutout = config['slack_shoutout']

        self.slack_text_prefix = 'System Error {shoutout}: '.format(
            shoutout=self.slack_shoutout)

        self.slack = Slacker(self.slack_api_token)

    def post_message(self, text):
        self.slack.chat.post_message(channel=self.slack_channel,
                                     text=''.join((self.slack_text_prefix,
                                                   text)),
                                     username=self.slack_username,
                                     icon_emoji=self.slack_emote)


def main():
    slack = Slack()
    slack.post_message('This is a test system state message, '
                       'please ignore me.')


if __name__ == '__main__':
    main()
