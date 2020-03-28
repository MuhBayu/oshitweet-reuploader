from dotenv import load_dotenv
load_dotenv()
import os
from pymongo import MongoClient
# Connect to the MongoDB, change the connection string per your MongoDB environment
client = MongoClient(os.getenv('MONNGO_URL'))
# Set the db object to point to the business database
db = client['fiony_backups']
media_collection = db['medias']
my_tweet_collection = db['my_tweets']
