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


if __name__ == "__main__":
    arg_names = ['command', 'tweet_id', 'debug']
    args = dict(zip(arg_names, sys.argv))
    tweet_id = args.get('tweet_id')
    if tweet_id is None:
        print("Please input tweet_id")
        sys.exit(0)
    status = twit.api.get_status(tweet_id)
    if args.get('debug'):
        print(status._json)
    if "extended_entities" in status._json:
        reupload(status)
