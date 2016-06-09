#!/usr/bin/env python
"""This file handles the communication to Slack.

Sends a message to Slack using the chat.postMessage API call.
"""

from slacker import Slacker


slack_api_token = 'xoxb-49168260642-Ex0cis6udHxPAHjWvB2HoQy2'  # The bots token
slack_username = "@systems.monitor"
slack_channel = '@sam.brennan'  # This would probably be the status channel
slack_emote = ':scream:'

slack_text = 'This is a test system state message, please ignore me.'


def post_message(slack, text):
    if slack:
        slack.chat.post_message(channel=slack_channel,
                                text=text,
                                username=slack_username,
                                icon_emoji=slack_emote)


def main():
    slack = Slacker(slack_api_token)

    post_message(slack, slack_text)


if __name__ == '__main__':
    main()
