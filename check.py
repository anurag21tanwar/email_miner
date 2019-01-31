import time
from utils.error import common_error_handler
from config.config import mongo_conf
import traceback
import pymongo
from datetime import datetime, timedelta
from utils.file import find_file_password
from utils.db import save_file_password, find_user_password, save_file_response


def check_password(email, file):
    try:
        if 'passwords' in email:
            pass_ = find_file_password(email['username'], email['passwords'], file)

            if pass_:
                save_file_password(file, pass_)
        else:
            u_pass_ = find_user_password(email['username'])

            if len(u_pass_) > 0:
                pass_ = find_file_password(email['username'], u_pass_, file)

                if pass_:
                    save_file_password(file, pass_)
    except Exception as e:
        print(traceback.print_exc())
        common_error_handler(e, email, file)


while True:
    client = pymongo.MongoClient(mongo_conf['server'], 27017)
    db = client[mongo_conf['db']]
    files_coll = db['files']
    emails_coll = db['emails']

    try:
        print('==CHECKING FOR NEW MESSAGES==')

        records = files_coll.find({'is_encrypted': 'True', 'state': 'in_progress', 'is_password': ''})

        for f in records:
            print('==FOUND==')
            e = emails_coll.find_one({'state': 'fetched', 'message_id': f['message_id']})

            if e is not None:
                if datetime.strptime(e['created_at'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=6) > datetime.today():
                    check_password(e, f)
                else:
                    save_file_response(f, [{'status': 'failed', 'status_message': 'Failed',
                                            'message': ['Password not found']},
                                           {'error_code': 'timeout', 'status_message': 'Failed',
                                            'message': ['File not uploaded']}])
            time.sleep(10)

    except Exception:
        print(traceback.print_exc())
    finally:
        client.close()
        time.sleep(60)
