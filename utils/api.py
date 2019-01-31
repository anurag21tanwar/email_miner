import requests
from utils.vault import fetch_word_cloud
from config.config import fetch_api_config
from utils.s3 import download_file_from_s3
from lib.error import *
import time
import base64
import pyotp


def generate_otp(key):
    str_ = str(base64.b32encode(key.encode())).split("'")[1].replace('=', '')
    if str:
        return pyotp.TOTP(str_).now()
    else:
        return


def get_token(url, otp, username, password, key):
    response = requests.post(url, data={'user[username]': username, 'user[password]': password})
    if response.status_code != 201:
        print('SESSION ERROR: {}, {}'.format(response, response.json()))
        raise InvalidCredentials('IC')
    else:
        jsondata = response.json()

        if jsondata['token'] and jsondata['login_flow'] == '2fa_verification':
            retry = 0
            while True:
                if retry < 2:
                    code = generate_otp(key)
                    if code:
                        response = requests.post(otp, data={'otp_code': code},
                                                 headers={'Authorization': jsondata['token']})
                        if response.status_code == 400:
                            print('OTP ERROR: {}, {}'.format(response, response.json()))
                            retry += 1
                        elif response.status_code != 201:
                            print('OTP ERROR: {}, {}'.format(response, response.json()))
                            raise InvalidOtp('IO')
                        else:
                            jsondata = response.json()
                            break
                    else:
                        return ''
                else:
                    print('OTP ERROR: {}, {}'.format(response, response.json()))
                    raise InvalidOtp('IO')
            return jsondata['token']
        else:
            return jsondata['token']


def send_file_for_anonymization(url, token, word_cloud, username, filename, password=None):
    subs = [("substitutions[{}]".format(key), value) for key, value in word_cloud.items()]
    file = [('documents[][file]', download_file_from_s3(username, filename))]

    if password:
        subs.append(('documents[][password]', password))

    response = requests.post(url, headers={'Authorization': token}, files=file, data=subs)

    if response.status_code != 201:
        print('ANONYMIZER ERROR: {}, {}'.format(response, response.json()))
        raise AnonymizationError('AE')
    else:
        return response.json()


def check_anonymization_status(url, doc_id, token):
    response = requests.get(url + '?document_ids={}'.format(doc_id), headers={'Authorization': token})

    if response.status_code != 200:
        print('ANONYMIZER STATUS ERROR: {}, {}'.format(response, response.json()))
        raise AnonymizationStatusError('ASE')
    else:
        return response.json()


def get_user_id(url, token, username):
    # username = 'canopy_demo'  # TODO: remove this line before deploying
    response = requests.get(url + '?page=1&per_page=20000', headers={'Authorization': token})

    if response.status_code != 200:
        print('USERS ID ERROR: {}, {}'.format(response, response.json()))
        raise UserIdError('UIE')
    else:
        users = response.json()['users']
        if len(users) > 0:
            for user in users:
                if username == user['username']:
                    return user['id']
            raise UserIdNotFound('UINF')
        else:
            raise UserIdNotFound('UINF')


def upload_anonymized_file(url, token, doc_id, user_id):
    response = requests.post(url, headers={'Authorization': token},
                             data={'documents[][id]': doc_id, 'documents[][report_type]': 'Statement',
                                   'document_user_ids': user_id})
    if response.status_code != 201:
        print('ANONYMIZER UPLOAD ERROR: {}, {}'.format(response, response.json()))
        raise AnonymizeUploadError('AUE')
    else:
        return response.json()


def validate_filename(url, file, token):
    response = requests.get(url + '?file_name={}'.format(file), headers={'Authorization': token})

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        return response.json()
    else:
        print('ERROR: {}, {}'.format(response, response.json()))
        raise ValidateFileNameError('VFNE')


def send_file_for_upload(url, username, file, user_id, token):
    response = requests.post(url + '?report_type=Analysis&document_user_ids={}'.format(user_id),
                             headers={'Authorization': token},
                             files={'attachment': download_file_from_s3(username, file)})
    if response.status_code != 201:
        print('UPLOAD ERROR: {}, {}'.format(response, response.json()))
        raise UploadError('UE')
    else:
        return response.json()


def send_file_to_api(username, file):
    api_config = fetch_api_config(username)
    token = get_token(api_config['session'], api_config['otp'], api_config['username'], api_config['password'],
                      api_config['key'])

    if file['is_pdf'] == 'True':
        if file['is_encrypted'] == 'False':
            res = validate_filename(api_config['validate'], file['filename'], token)

            if str(res) == 'True':
                word_cloud = fetch_word_cloud(username)
                anony_res = send_file_for_anonymization(api_config['anonymize'], token, word_cloud, username,
                                                        file['filename'])
            else:
                anony_res = [{'status': 'failed', 'status_message': 'Failed', 'message': res['error']}]

        elif file['is_encrypted'] == 'True':
            if 'is_password' in file and file['is_password']:
                res = validate_filename(api_config['validate'], file['filename'], token)

                if str(res) == 'True':
                    word_cloud = fetch_word_cloud(username)
                    anony_res = send_file_for_anonymization(api_config['anonymize'], token, word_cloud, username,
                                                            file['filename'], file['is_password'])
                else:
                    anony_res = [{'status': 'failed', 'status_message': 'Failed', 'message': res['error']}]
            else:
                return

        time.sleep(2)

        while True:
            if anony_res[0]['status'] == 'in_progress' and anony_res[0]['status_message'] == 'Converting':
                r = check_anonymization_status(api_config['anonymize_s'], anony_res[0]['id'], token)
                anony_res = r
                time.sleep(0.25)
            else:
                anony_s_res = anony_res[0]
                break

        user_id = get_user_id(api_config['users'], token, username)

        if anony_s_res['status'] == 'ready' and anony_s_res['status_message'] == 'Success':
            r = upload_anonymized_file(api_config['anonymize_u'], token, anony_s_res['id'], user_id)

            if str(r) == 'True':
                anony_u_res = {'status_message': 'Success', 'message': ['File uploaded']}
            else:
                print('ANONYMIZER UPLOAD ERROR: {}, {}'.format(r, anony_s_res['id']))
                anony_u_res = {'status_message': 'Failed', 'message': ['File not uploaded']}
        else:
            anony_u_res = {'status_message': 'Failed', 'message': ['File not uploaded']}

        return [anony_s_res, anony_u_res]

    if file['is_pdf'] == 'False':
        user_id = get_user_id(api_config['users'], token, username)

        res = validate_filename(api_config['validate'], file['filename'], token)

        if str(res) == 'True':
            r = send_file_for_upload(api_config['upload'], username, file['filename'], user_id, token)

            if str(r) == 'True':
                upload_res = {'status_message': 'Success', 'message': ['File uploaded']}
            else:
                upload_res = {'status_message': 'Failed', 'message': ['File not uploaded']}
        else:
            upload_res = {'status_message': 'Failed', 'message': res['error']}

        return ['NA', upload_res]
