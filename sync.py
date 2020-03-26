#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Run this script for initialization
"""

from dotenv import load_dotenv
load_dotenv()

import tweepy
import requests
import os
import time
from util import Mongo
from util.Twitter import twit
from handler.media import reupload


def isMultipleof10(n):
    s = str(n)
    l = len(s)
    if s[l - 1] == '10' or s[l - 1] == '0':
        return True
    return False


def get_all_tweets(screen_name):
    user = twit.api.get_user(screen_name=screen_name)
    alltweets = []
    new_tweets = twit.api.user_timeline(screen_name=screen_name, count=1)
    alltweets.extend(new_tweets)
    oldest = alltweets[-1].id - 1

    while len(new_tweets) > 0:
        print('getting tweets before %s' % oldest)
        new_tweets = twit.api.user_timeline(
            screen_name=screen_name, count=200, max_id=oldest)

        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1

        print('...%s tweets downloaded so far' % len(alltweets))

    outtweets = []  # initialize master list to hold our ready tweets
    i = 1
    for tweet in reversed(alltweets):
        try:
            if 'extended_entities' in tweet._json:
                i += 1
                if isMultipleof10(i) == True:
                    time.sleep(10)
                reupload(tweet)
        except Exception as e:
            print(str(e))


if __name__ == '__main__':
    get_all_tweets(os.getenv('OSHI_USERNAME'))