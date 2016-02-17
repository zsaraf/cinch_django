from django.core.management.base import BaseCommand, CommandError
from urllib import urlopen
import time
from sesh import slack_utils

class Command(BaseCommand):
    help = 'Pings sesh server'

    def add_arguments(self, parser):

while True:
    try:
        urlopen("https://seshtutorin.com")
    except:
        slack_utils.send_slack_message("*URGENT: THE SERVER IS DOWN*", True)
        pass
    time.sleep(60)
