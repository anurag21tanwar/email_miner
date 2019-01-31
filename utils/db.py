import pymongo
from datetime import datetime
from config.config import mongo_conf
from lib.error import FileHandleError, MongoError
from utils.file import check_upload_pdf, upload_non_pdf

supported_file_formats = ['application/vnd.ms-excel',
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                          'application/msword',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'application/vnd.ms-powerpoint',
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                          'application/x-ole-storage',
                          'text/plain',
                          'text/csv',
                          'image/png',
                          'image/jpeg']


def create_email_record(data):
    client = pymongo.MongoClient(mongo_conf['server'], 27017)
    db = client[mongo_conf['db']]
    collection = db['emails']

    data.update({'created_at': datetime.today().strftime('%Y-%m-%d %H:%M:%S'), 'state': 'fetched'})

    try:
        collection.insert_one(data)
    except:
        raise MongoError('ME')
    finally:
        client.close()


def save_email_password(data):
    client = pymongo.MongoClient(mongo_conf['server'], 27017)
    db = client[mongo_conf['db']]
    email_coll = db['emails']
    pass_coll = db['passwords']

    try:
        e = email_coll.find_one({'subject': data['subject'], 'username': data['username'], 'state': 'fetched'})

        if e is not None:
            e['passwords'] = list(set(data['passwords']))
            email_coll.save(e)
        else:
            p = pass_coll.find_one({'username': data['username']})

            if p is not None:
                p['passwords'] = list(set(p['passwords'] + data['passwords']))
                pass_coll.save(p)
            else:
                pass_coll.insert_one({'username': data['username'], 'passwords': data['passwords']})
    except:
        raise MongoError('ME')
    finally:
        client.close()


def create_file_record(data):
    client = pymongo.MongoClient(mongo_conf['server'], 27017)
    db = client[mongo_conf['db']]
    collection = db['files']

    try:
        ctype = data['attachment']['mail_content_type']
        filename = data['attachment']['filename']

        if ctype == 'application/pdf':
            res = check_upload_pdf(data['username'], data['attachment'])
            dict_ = {'filename': filename, 'content_type': ctype, 'is_pdf': res[1], 'is_encrypted': res[2],
                     'is_password': res[3], 'state': 'in_progress'}
        elif ctype in supported_file_formats:
            res = upload_non_pdf(data['username'], data['attachment'])
            dict_ = {'filename': filename, 'content_type': ctype, 'is_pdf': res[1], 'is_encrypted': res[2],
                     'is_password': res[3], 'state': 'in_progress'}
        else:
            dict_ = {'filename': filename, 'content_type': ctype, 'is_pdf': 'False', 'is_encrypted': 'False',
                     'is_password': 'NA', 'state': 'completed',
                     'response': {'anonymize': 'NA',
                                  'upload': {"status_message": "Failed", "message": ["Unsupported Format"]}}}

        dict_.update({'message_id': data['message_id'], 'created_at': datetime.today().strftime('%Y-%m-%d %H:%M:%S')})
    except:
        raise FileHandleError('FHE')
    finally:
        client.close()

    try:
        collection.insert_one(dict_)
    except:
        raise MongoError('ME')
    finally:
        client.close()


def save_file_response(file, res):
    client = pymongo.MongoClient(mongo_conf['server'], 27017)
    db = client[mongo_conf['db']]
    collection = db['files']

    try:
        if file is not None:
            file['state'] = 'completed'
            file['response'] = {'anonymize': res[0], 'upload': res[1]}
            collection.save(file)
    except:
        raise MongoError('ME')
    finally:
        client.close()


def save_file_password(file, password):
    client = pymongo.MongoClient(mongo_conf['server'], 27017)
    db = client[mongo_conf['db']]
    collection = db['files']

    try:
        if file is not None:
            file['is_password'] = password
            collection.save(file)
    except:
        raise MongoError('ME')
    finally:
        client.close()


def save_email_response(email):
    client = pymongo.MongoClient(mongo_conf['server'], 27017)
    db = client[mongo_conf['db']]
    collection = db['emails']

    try:
        if email is not None:
            email['state'] = 'responded'
            collection.save(email)
    except:
        raise MongoError('ME')
    finally:
        client.close()


def find_user_password(username):
    client = pymongo.MongoClient(mongo_conf['server'], 27017)
    db = client[mongo_conf['db']]
    collection = db['passwords']

    try:
        p = collection.find_one({'username': username})

        if p is not None:
            return p['passwords']
        else:
            return []
    except:
        raise MongoError('ME')
    finally:
        client.close()
