import os
import requests
import json
from util import Mongo
from util.Twitter import twit
from util.s3 import upload_to_aws
from datetime import datetime


def reupload(tweet):
	media_paths = []
	status = f"from Twitter ({tweet.created_at})"
	year_and_month = tweet.created_at.strftime("%Y/%b")
	video_dl = ''
	for med in tweet._json['extended_entities']['media']:
		if med['type'] == 'photo':
			media_url = med['media_url']
		else:
			get_index_video_url = -1 if med['video_info']['variants'][-1][
				'content_type'] == 'video/mp4' else -2
			media_url = med['video_info']['variants'][get_index_video_url][
				'url']

		r = requests.get(media_url, allow_redirects=True)
		fName = os.path.basename(media_url)
		fName = fName.split('?', maxsplit=1)[0]
		images_folder = f"./medias/{tweet.user.screen_name}"

		if not os.path.exists(images_folder):
			os.mkdir(images_folder)

		if len(tweet._json['extended_entities']['media']) > 1:
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
				"media_url": media_url,
				"media_type": med['type'],
				"media_path": dir_name,
				"created_at": tweet.created_at
			}
			Mongo.media_collection.insert_one(data_insert)

		f = open(dir_name, 'wb')
		f.write(r.content)
		f.close()

		upload_s3 = upload_to_aws(dir_name, year_and_month)
		if med['type'] == 'video':
			video_dl = upload_s3
    
		media_type = r.headers.get('content-type')
		print(f"{media_url} -> {media_type}")

		del r

	if media_paths:
		if Mongo.my_tweet_collection.find_one({"reupload_tweet_id": tweet.id_str }):
			print(f"{tweet.id_str} Tweet is duplicate")
			return False
		update_status = twit.update_status_media_upload(
			status, media_paths, media_type)
		if update_status is not None:
			if video_dl:
				twit.api.update_status(
					status=f"Download disini {video_dl}",
					in_reply_to_status_id=update_status.id_str,
					auto_populate_reply_metadata=True)
			my_tweet_insert = {
				"id": update_status.id_str,
				"reupload_tweet_id": tweet.id_str,
				"text": status,
				"media_paths": json.dumps(media_paths),
				"created_at": update_status.created_at
			}
			Mongo.my_tweet_collection.insert_one(my_tweet_insert)
			clear_file(media_paths)
			return True
		else:
			clear_file(media_paths)
			print("Update status gagal")
			return False
	return False

def clear_file(paths):
	if os.getenv('PY_ENV', 'development') == 'development':
		return False
	for filename in paths:
		if os.path.exists(filename):
			os.unlink(filename)