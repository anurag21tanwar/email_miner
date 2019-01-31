import boto3
import os
from os.path import join
from config.config import s3_conf


def download_file_from_s3(username, filename):
    s3 = boto3.resource('s3')
    s3.Bucket(s3_conf['bucket']).download_file(join(username, filename), join('tmp', filename))
    file = open(join('tmp', filename), 'rb')
    os.remove(join('tmp', filename))
    return file


def upload_file_to_s3(username, attachment):
    s3 = boto3.resource('s3')
    s3.Object(s3_conf['bucket'], join(username, attachment['filename'])).put(
        Body=open(join('tmp', attachment['filename']), 'rb'),
        ContentType=attachment[
            'mail_content_type'])
