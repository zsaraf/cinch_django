from slacker import Slacker
from django.conf import settings

slack = Slacker(settings.SLACK_BOT_TOKEN)


def send_simple_slack_message(message):
    # post to slack TODO add detail
    send_slack_message(message, False)


def send_slack_message(message, force_send):
    # post to slack TODO add detail
    try:
        if settings.DEBUG is False or force_send:
            slack.chat.post_message(settings.SLACK_CHANNEL, message, as_user=True)
    except:
        pass
