import time
from utils.error import common_error_handler
from config.config import mongo_conf
import traceback
import pymongo
from utils.sendgrid import send_email_user
from utils.db import save_email_response, save_file_response
from datetime import datetime, timedelta


def send_response(email, files):
    try:
        r = send_email_user(email, files)

        if r:
            save_email_response(email)

    except Exception as e:
        print(traceback.print_exc())
        common_error_handler(e, email, None)


while True:
    client = pymongo.MongoClient(mongo_conf['server'], 27017)
    db = client[mongo_conf['db']]
    files_coll = db['files']
    emails_coll = db['emails']

    try:
        print('==CHECKING FOR NEW MESSAGES==')

        records = emails_coll.find({'state': 'fetched'})

        for e in records:
            print('==FOUND==')
            rec = files_coll.find({'message_id': e['message_id']})

            if datetime.strptime(e['created_at'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=6) > datetime.today():
                is_ready, files = True, []

                for f in rec:
                    files.append(f)
                    if f['state'] != 'completed':
                        is_ready = False
                        break

                if is_ready and len(files) > 0:
                    send_response(e, files)
            else:
                for f in rec:
                    if f['state'] == 'in_progress' and f['is_pdf'] == 'False':
                        save_file_response(f, ['NA', {'error_code': 'timeout', 'status_message': 'Failed',
                                                      'message': ['File not uploaded']}])

            time.sleep(10)

    except Exception:
        print(traceback.print_exc())
    finally:
        client.close()
        time.sleep(60)
