from urllib import urlopen
import time
from sesh import slack_utils

while True:
    try:
        urlopen("https://seshtutorin.com")
    except:
        slack_utils.send_slack_message("*URGENT: THE SERVER IS DOWN*", True)
        pass
    time.sleep(60)
