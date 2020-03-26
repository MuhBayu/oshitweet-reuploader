from dotenv import load_dotenv
load_dotenv()
import json
import os
import sys
from util.Twitter import twit
from handler.media import reupload

TWIT_CONSUMER_TOKEN = os.getenv('CONSUMER_KEY')
TWIT_CONSUMER_SECRET = os.getenv('SECRET_KEY')

TWIT_ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
TWIT_ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

SCREEN_NAME = os.getenv('OSHI_USERNAME')

status = twit.api.get_status('1235829307554988032')
reupload(status)
