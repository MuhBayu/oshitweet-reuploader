import os
import requests
import json
from util import Mongo
from util.Twitter import twit
from util.s3 import upload_to_aws
from datetime import datetime
import mimetypes

def reupload(tweet):
	media_paths = []
	caption = f"from Twitter ({tweet.created_at})\n\nhttps://twitter.com/{tweet.author.screen_name}/status/{tweet.id_str}"
	year_and_month = tweet.created_at.strftime("%Y/%b")
	video_dl = ''
	tweetJson = tweet._json
	is_tgif = False

	if "text" in tweetJson:
		text = tweetJson['text']
	elif "full_text" in tweetJson:
		text = tweetJson['full_text']

	def biggest_bitrate(variants):
		bitrate = []
		for v in variants['variants']:
			bitrate.append(v['bitrate'] if "bitrate" in v else 0)
		index = bitrate.index(max(bitrate)) if len(bitrate) > 0 else -1
		return variants['variants'][index]['url']

	if "entities" in tweetJson:
		if "hashtags" in tweetJson['entities']:
			for h in tweetJson['entities']['hashtags']:
				if h['text'] == 'TGIF':
					is_tgif = True

	for med in tweetJson['extended_entities']['media']:
		media_url = med['media_url'] if med['type'] == 'photo' else biggest_bitrate(med['video_info'])
		thumbnail = med['media_url_https']

		fName = os.path.basename(media_url)
		fName = fName.split('?', maxsplit=1)[0]
		images_folder = f"./medias/{tweet.user.screen_name}/{year_and_month}"

		if not os.path.exists(images_folder):
			os.makedirs(images_folder)

		if len(tweetJson['extended_entities']['media']) > 1:
			folder_dir = '{}/{}'.format(images_folder, tweet.id_str)
			if not os.path.exists(folder_dir):
				os.mkdir(folder_dir)
			dir_name = '{}/{}'.format(folder_dir, fName)
		else:
			dir_name = '{}/{}'.format(images_folder, fName)

		media_paths.append(dir_name)

		if Mongo.media_collection.find_one({"id": tweet.id_str, "media_url": media_url}):
			print(f"Media tweet {tweet.id_str} sudah ada")
		else:
			data_insert = {
				"id": tweet.id_str,
				"text": text,
				"media_url": media_url,
				"thumbnail": thumbnail,
				"media_type": med['type'],
				"media_path": dir_name,
				"created_at": tweet.created_at,
				"is_tgif": is_tgif
			}
			Mongo.media_collection.insert_one(data_insert)

		media_type = None
		if not os.path.exists(dir_name):
			r = requests.get(media_url, allow_redirects=True)
			media_type = r.headers.get('content-type')
			f = open(dir_name, 'wb')
			f.write(r.content)
			f.close()
			del r
			print(f">> [{tweet.id_str}] {media_url} ({media_type}) -> DOWNLOADED")
		else:
			media_type = mimetypes.MimeTypes().guess_type(dir_name)[0]	
			print(f"[{tweet.id_str}] {media_url} ({media_type}) -> SKIPPED")

		upload_s3 = upload_to_aws(dir_name, year_and_month)
		if med['type'] == 'video':
			video_dl = upload_s3

	if media_paths:
		if Mongo.my_tweet_collection.find_one({"reupload_tweet_id": tweet.id_str }):
			print(f"{tweet.id_str} Tweet is duplicate")
			return False
		update_status = twit.update_status_media_upload(
			caption, media_paths, media_type)
		if update_status is not None:
			if video_dl:
				twit.api.update_status(
					status=f"Download disini {video_dl}",
					in_reply_to_status_id=update_status.id_str,
					auto_populate_reply_metadata=True)
			my_tweet_insert = {
				"id": update_status.id_str,
				"reupload_tweet_id": tweet.id_str,
				"text": caption,
				"media_paths": json.dumps(media_paths),
				"created_at": update_status.created_at
			}
			Mongo.my_tweet_collection.insert_one(my_tweet_insert)
			clean_file(media_paths)
			return True
		else:
			clean_file(media_paths)
			print("Update status gagal")
			return False
	return False

def clean_file(paths):
	if os.getenv('PY_ENV', 'development') == 'development':
		return False
	for filename in paths:
		if os.path.exists(filename):
			os.unlink(filename)
