from slacker import Slacker
from sesh import settings

slack = Slacker(settings.SLACK_BOT_TOKEN)


def send_simple_slack_message(message):
    # post to slack TODO add detail
    try:
        slack.chat.post_message(settings.SLACK_CHANNEL, message, as_user=True)
    except:
        pass
