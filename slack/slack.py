#!/usr/bin/env python
"""This file handles the communication to Slack.

Sends a message to Slack using the chat.postMessage API call.
"""

from slacker import Slacker


class Slack:
    # TODO - Move all these settings into config
    # The bots token
    slack_api_token = 'xoxb-49168260642-Ex0cis6udHxPAHjWvB2HoQy2'
    slack_username = "@systems.monitor"
    slack_channel = '#status'  # '@sam.brennan'  #
    slack_emote = ':scream:'
    slack_shoutout = '@devs'

    slack_text_prefix = 'System Error {shoutout}: '.format(
        shoutout=slack_shoutout)

    slack = Slacker(slack_api_token)

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
