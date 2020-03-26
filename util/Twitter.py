import os
import time
import tweepy
import requests
from requests_oauthlib import OAuth1

class Twitter:
	def __init__(self, consumer_key, secret_key, access_token, access_secret):
		auth = tweepy.OAuthHandler(consumer_key, secret_key)
		auth.set_access_token(access_token, access_secret)
		self._api = tweepy.API(auth)
		self._oauth1 = OAuth1(consumer_key, client_secret=secret_key, resource_owner_key=access_token, resource_owner_secret=access_secret)

	def update_status_media_upload(self, status, medias, media_type):
		try:
			media_ids = []
			if media_type in ['video/mp4', 'video/mkv']:
				media_path = os.path.abspath(medias[-1])
				return self.upload_video(status, media_path)

			for filename in medias:
				media_path = os.path.abspath(filename)
				res = self._api.media_upload(filename)
				media_ids.append(res.media_id)
			post = {"status": status} if len(medias) < 1 else {"status": status, "media_ids": media_ids}
			return self._api.update_status(**post)
		except tweepy.TweepError as e:
			print(str(e))
			return None
		except Exception as ex:
			print(str(ex))
			return None
	
	def upload_video(self, status, filename):
		try:
			videoTweet = VideoTweet(self._oauth1, filename)
			videoTweet.upload_init()
			videoTweet.upload_append()
			videoTweet.upload_finalize()
			update = videoTweet.tweet(status)
			return self.api.get_status(update['id_str'])
		except Exception as e:
			return None

	@property
	def api(self):
		return self._api


class VideoTweet(object):
	MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
	POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'
	
	def __init__(self, oauth, file_name):
		'''
		Defines video tweet properties
		'''
		self.video_filename = file_name
		self.total_bytes = os.path.getsize(self.video_filename)
		self.media_id = None
		self.processing_info = None
		self.oauth = oauth


	def upload_init(self):
		'''
		Initializes Upload
		'''
		print('INIT')

		request_data = {
			'command': 'INIT',
			'media_type': 'video/mp4',
			'total_bytes': self.total_bytes,
			'media_category': 'tweet_video'
		}

		req = requests.post(url=self.MEDIA_ENDPOINT_URL, data=request_data, auth=self.oauth)
		media_id = req.json()['media_id']

		self.media_id = media_id

		print('Media ID: %s' % str(media_id))


	def upload_append(self):
		'''
		Uploads media in chunks and appends to chunks uploaded
		'''
		segment_id = 0
		bytes_sent = 0
		file = open(self.video_filename, 'rb')

		while bytes_sent < self.total_bytes:
			chunk = file.read(4*1024*1024)
			
			print('APPEND')

			request_data = {
				'command': 'APPEND',
				'media_id': self.media_id,
				'segment_index': segment_id
			}

			files = {
				'media':chunk
			}

			req = requests.post(url=self.MEDIA_ENDPOINT_URL, data=request_data, files=files, auth=self.oauth)

			if req.status_code < 200 or req.status_code > 299:
				print(req.status_code)
				print(req.text)
				sys.exit(0)

			segment_id = segment_id + 1
			bytes_sent = file.tell()

			print('%s of %s bytes uploaded' % (str(bytes_sent), str(self.total_bytes)))

		print('Upload chunks complete.')


	def upload_finalize(self):
		'''
		Finalizes uploads and starts video processing
		'''
		print('FINALIZE')

		request_data = {
			'command': 'FINALIZE',
			'media_id': self.media_id
		}

		req = requests.post(url=self.MEDIA_ENDPOINT_URL, data=request_data, auth=self.oauth)

		self.processing_info = req.json().get('processing_info', None)
		self.check_status()
		return req.json()


	def check_status(self):
		'''
		Checks video processing status
		'''
		if self.processing_info is None:
			return

		state = self.processing_info['state']

		print('Media processing status is %s ' % state)

		if state == u'succeeded':
			return

		if state == u'failed':
			sys.exit(0)

		check_after_secs = self.processing_info['check_after_secs']

		print('Checking after %s seconds' % str(check_after_secs))
		time.sleep(check_after_secs)

		print('STATUS')

		request_params = {
			'command': 'STATUS',
			'media_id': self.media_id
		}

		req = requests.get(url=self.MEDIA_ENDPOINT_URL, params=request_params, auth=self.oauth)

		self.processing_info = req.json().get('processing_info', None)
		self.check_status()
		return req.json()


	def tweet(self, status):
		'''
		Publishes Tweet with attached video
		'''
		request_data = {
			'status': status,
			'media_ids': self.media_id
		}

		req = requests.post(url=self.POST_TWEET_URL, data=request_data, auth=self.oauth)
		return req.json()

TWIT_CONSUMER_TOKEN = os.getenv('CONSUMER_KEY')
TWIT_CONSUMER_SECRET = os.getenv('SECRET_KEY')

TWIT_ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
TWIT_ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

twit = Twitter(TWIT_CONSUMER_TOKEN, TWIT_CONSUMER_SECRET, TWIT_ACCESS_TOKEN, TWIT_ACCESS_TOKEN_SECRET)