"""Custom S3 storage backends to store files in subfolders."""
import boto
from boto.s3.key import Key
import os
from django.conf import settings
from StringIO import StringIO
import urllib2


def get_true_image_size(fp):
    from PIL import Image
    from PIL.ExifTags import TAGS

    image = Image.open(fp)

    exifdict = image._getexif()
    if len(exifdict):
        for k in exifdict.keys():
            if k in TAGS.keys() and TAGS[k] == 'Orientation':
                orientation = exifdict[k]
                if orientation > 4:
                    # flip if should be horizontal
                    return (image.height, image.width)

    return (image.width, image.height)


def get_resized_image(self, fp, size):
    from PIL import Image
    from StringIO import StringIO

    fp.seek(0)
    image = Image.open(fp)
    image.thumbnail(size, Image.ANTIALIAS)
    new_fp = StringIO()
    image.save(new_fp, 'JPEG')
    new_fp.seek(0)

    return new_fp


def get_file_from_s3(path, file_name):
    url = settings.S3_URL + "/" + os.path.join(path, file_name)
    try:
        response = urllib2.urlopen(url)
        fp = StringIO(response.read())
        return fp
    except Exception:
        return False


def upload_image_to_s3(fp, path, file_name):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    # connect to the bucket
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucket_name)

    full_key_name = os.path.join(path, file_name)

    # create a key to keep track of our file in the storage
    k = Key(bucket)
    k.key = full_key_name
    k.content_type = 'image/jpeg'
    k.set_contents_from_file(fp)

    # we need to make it public so it can be accessed publicly
    # using a URL like http://sesh-tutoring-dev.s3.amazonaws.com/file_name.png
    k.make_public()

    url = settings.S3_URL + "/" + full_key_name
    return url
