"""Custom S3 storage backends to store files in subfolders."""
import boto
from boto.s3.key import Key
import os
from django.conf import settings


def upload_png_to_s3(fp, path, file_name):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    # connect to the bucket
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucket_name)

    full_key_name = os.path.join(path, file_name)

    # create a key to keep track of our file in the storage
    k = Key(bucket)
    k.key = full_key_name
    k.content_type = 'image/png'
    k.set_contents_from_file(fp)

    # we need to make it public so it can be accessed publicly
    # using a URL like http://sesh-tutoring-dev.s3.amazonaws.com/file_name.png
    k.make_public()

    url = settings.S3_URL + "/" + full_key_name
    return url
