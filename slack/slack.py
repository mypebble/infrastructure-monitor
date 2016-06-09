#!/usr/bin/env python
"""This file handles the communication to Slack.

Sends a message to Slack using the chat.postMessage API call.
"""

from slacker import Slacker


class Slack:
    # The bots token TODO - Take out of config
    slack_api_token = 'xoxb-49168260642-Ex0cis6udHxPAHjWvB2HoQy2'
    slack_username = "@systems.monitor"
    # TODO - set to the status channel
    slack_channel = '@sam.brennan'
    slack_emote = ':scream:'
    slack_shoutout = '@devs'

    # TODO - switch over to slack_shoutout
    slack_text_prefix = 'System Error {shoutout}: '.format(shoutout=slack_channel)

    slack = Slacker(slack_api_token)

    def post_message(self, text):
        self.slack.chat.post_message(channel=self.slack_channel,
                                     text=''.join((self.slack_text_prefix, text)),
                                     username=self.slack_username,
                                     icon_emoji=self.slack_emote)


def main():
    slack = Slack()
    slack.post_message('This is a test system state message, please ignore me.')


if __name__ == '__main__':
    main()
