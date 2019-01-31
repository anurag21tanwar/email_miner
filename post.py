import time
from utils.api import send_file_to_api
from utils.error import common_error_handler
from utils.db import save_file_response
from config.config import mongo_conf
import traceback
import pymongo


def process_file(email, file):
    try:
        res = send_file_to_api(email['username'], file)

        if res:
            save_file_response(file, res)
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

        records = files_coll.find({'state': 'in_progress'})

        for f in records:
            e = emails_coll.find_one({'state': 'fetched', 'message_id': f['message_id']})

            if e is not None:
                print('==FOUND==')
                process_file(e, f)

            time.sleep(10)

    except Exception:
        print(traceback.print_exc())
    finally:
        client.close()
        time.sleep(60)
