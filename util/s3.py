import os
import boto3
from botocore.exceptions import NoCredentialsError

ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
SECRET_KEY = os.getenv('S3_SECRET_KEY')
BUCKET_NAME = os.getenv('S3_BUCKET')

def upload_to_aws(local_file, folder_name):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    try:
        key_name = f"{folder_name}/{os.path.basename(local_file)}"
        local_path = os.path.abspath(local_file)
        s3.upload_file(local_path, BUCKET_NAME, key_name)
        s3.put_object_acl(ACL='public-read', Bucket=BUCKET_NAME, Key=key_name)
        bucket_location = s3.get_bucket_location(Bucket=BUCKET_NAME)
        object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(bucket_location['LocationConstraint'], BUCKET_NAME, key_name)
        print("Upload Successful")
        return object_url
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False