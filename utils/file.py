from utils.s3 import upload_file_to_s3, download_file_from_s3
from pikepdf import Pdf
import base64
import os
from os.path import join


def decode_file(attachment):
    if attachment['content_transfer_encoding'] == 'base64':
        open(join('tmp', attachment['filename']), 'wb').write(base64.b64decode(attachment['payload']))
    else:
        open(join('tmp', attachment['filename']), 'wb').write(attachment['payload'].encode('utf-8'))


def check_upload_pdf(username, attachment):
    decode_file(attachment)
    upload_file_to_s3(username, attachment)

    try:
        Pdf.open(open(join('tmp', attachment['filename']), 'rb'), '')
        return [attachment['filename'], 'True', 'False', 'NA']
    except:
        return [attachment['filename'], 'True', 'True', '']
    finally:
        os.remove(join('tmp', attachment['filename']))


def upload_non_pdf(username, attachment):
    decode_file(attachment)
    upload_file_to_s3(username, attachment)
    os.remove(join('tmp', attachment['filename']))
    return [attachment['filename'], 'False', 'False', 'NA']


def find_file_password(username, passwords, file):
    f = download_file_from_s3(username, file['filename'])

    for p in passwords:
        try:
            Pdf.open(f, p)
            return p
        except:
            pass
