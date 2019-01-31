import sendgrid
from config.config import sendgrid_conf, fetch_api_config
from lib.error import SendGridError


def send_email_user(email, files):
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_conf['api_key'])
    api_config = fetch_api_config(email['username'])
    data = {
        'from': {
            'email': 'no-reply@myapp.org'
        },
        'personalizations': [
            {
                'to': [
                    {
                        'email': email['mail_from']
                    }
                ],
                'dynamic_template_data': {
                    'name': email['username'],
                    'logo': 'https://secure.myapp.org/branding/login_logo.png',
                    'footer_email': 'mailto:connect@myapp.org',
                    'footer_about': 'https://myapp.org/about/',
                    'footer_support': 'https://support.myapp.org/',
                    'footer_terms': 'https://myapp.org/terms_and_privacy.html',
                    'footer_contact': 'mailto:connect@myapp.org',
                    'app_name': api_config['app'],
                    'app_env': api_config['env'],
                    'horizontal_line': api_config['line'],
                    'fb': api_config['fb'],
                    'twitter': api_config['twitter'],
                    'linkedin': api_config['linkedin'],
                    'mail': api_config['mail'],
                    'host': api_config['host']
                }
            }
        ],
        'template_id': 'd-78e89ed44e2d466ea542d53e4ff2252a'
    }

    pdf, non_pdf = {'pdf': []}, {'non_pdf': []}

    for file in files:
        if file['is_pdf'] == 'True':
            pdf['pdf'].append({'file': file['filename'],
                               'anonymize': '{}:{}'.format(file['response']['anonymize']['status_message'],
                                                           file['response']['anonymize']['message']),
                               'upload': '{}:{}'.format(file['response']['upload']['status_message'],
                                                        file['response']['upload']['message'])})
        elif file['is_pdf'] == 'False':
            non_pdf['non_pdf'].append({'file': file['filename'], 'anonymize': 'NA',
                                       'upload': '{}:{}'.format(file['response']['upload']['status_message'],
                                                                file['response']['upload']['message'])})

    data['personalizations'][0]['dynamic_template_data'].update(pdf)
    data['personalizations'][0]['dynamic_template_data'].update(non_pdf)

    response = sg.client.mail.send.post(request_body=data)
    if str(response.status_code).startswith('4') or str(response.status_code).startswith('5'):
        print('SENDGRID ERROR: {}, {}'.format(response, response.json()))
        raise SendGridError('SGE')
    else:
        return True
