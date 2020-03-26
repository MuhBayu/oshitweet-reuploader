#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author: https://github.com/MuhBayu
Date: 2020-03-27
"""

from dotenv import load_dotenv
load_dotenv()
import json
import os
from util.Twitter import tweepy, twit
from handler.media import reupload

TWIT_CONSUMER_TOKEN = os.getenv('CONSUMER_KEY')
TWIT_CONSUMER_SECRET = os.getenv('SECRET_KEY')

TWIT_ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
TWIT_ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

SCREEN_NAME = os.getenv('OSHI_USERNAME')


class MyStreamListener(tweepy.StreamListener):
    
    def __init__(self, api):
        super(MyStreamListener, self).__init__()
        self._api = api

    def on_data(self, data):
        data = json.loads(data)
        if 'user' in data:
            status = self._api.get_status(data['id_str'])
            if status:
                print(status)
                reupload(status)
        else:
            print(data)

    def on_status(self, status):
        print(status)

    def on_disconnect(self):
        print('Disconnected')

    def on_error(self, status_code):
        if status_code == 420:
            print('The App Is Being Rate Limited For Making Too Many Requests')
            os.unlink(pidfile)
        else:
            print('Error {}n'.format(status))
        return True


if __name__ == '__main__':
    pidfile = 'streamapp.pid'
    f = open(pidfile, 'w')
    f.write(str(os.getpid()))
    f.close()
    try:
        myStream = tweepy.Stream(auth=twit.api.auth,
                                 listener=MyStreamListener(twit.api))
        user = twit.api.get_user(screen_name=SCREEN_NAME)
        print('Service running, CTRL+C to stop')
        myStream.filter(follow=[user.id_str])
    except Exception as e:
        print(str(e))
    except KeyboardInterrupt:
        print('Stopped.')
    finally:
        print('Done.')
        if os.path.isfile(pidfile):
            os.unlink(pidfile)
        myStream.disconnect()

			