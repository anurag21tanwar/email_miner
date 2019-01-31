from dotenv import load_dotenv
import os

load_dotenv()

mail_conf = {
    'email': os.getenv('MAIL_ADDR'),
    'password': os.getenv('MAIL_PASS'),
    'server': 'imap.gmail.com',
    'port': 993
}

mongo_conf = {
    'server': os.getenv('MONGO_HOST'),
    'db': '' + os.getenv('ENV')
}

s3_conf = {
    'bucket': 'my-files'
}

vault_conf = {
    'server': 'http://127.0.0.1:8200',
    'connection_mode': 'token',
    'token': os.getenv('VAULT_TOKEN')
}

sendgrid_conf = {
    'api_key': os.getenv('SENDGRID_KEY')
}


def api_conf(app, host):
    h = {
        'username': os.getenv('API_USER'),
        'password': os.getenv('API_PASS'),
        'key': os.getenv('API_KEY'),
        'session': host[0] + '/api/v1/sessions',
        'otp': host[0] + '/api/v1/sessions/otp/validate',
        'anonymize': host[0] + '/api/v1/anonymize/create',
        'anonymize_s': host[0] + '/api/v1/anonymize/status',
        'anonymize_u': host[0] + '/api/v1/anonymize/upload',
        'users': host[0] + '/api/v1/admin/users',
        'upload': host[0] + '/api/v1/uploads/create',
        'validate': host[0] + '/api/v1/uploads/validate_name',
        'line': host[0] + '/myapp/images/horizontal_line-icon.png',
        'fb': {'src': host[0] + '/myapp/images/fb.png', 'url': 'https://www.facebook.com/myapp.org'},
        'twitter': {'src': host[0] + '/myapp/images/twitter.png', 'url': 'https://twitter.com/myapp.org'},
        'linkedin': {'src': host[0] + '/myapp/images/linkedin.png',
                     'url': 'https://www.linkedin.com/company/myapp.org/'},
        'mail': {'src': host[0] + '/myapp/images/mail.png', 'url': host[2]},
        'app': app,
        'host': host[1]
    }
    if os.getenv('ENV') != 'Production':
        h.update({'env': '[{}] '.format(os.getenv('ENV'))})
    return h


def find_host(app, env):
    if app == 'ML':
        if env == 'Test':
            return ['https://testing-api.myapp.org', 'https://myapp-testing.myapp.org', 'connect@myapp.org']
        elif env == 'Staging':
            return ['https://staging-api.myapp.org', 'https://myapp-staging.myapp.org', 'connect@myapp.org']
        elif env == 'Production':
            return ['https://api.myapp.org', 'https://secure.myapp.org', 'connect@myapp.org']
        else:
            return ['https://dev-api.myapp.org', 'https://myapp-dev.myapp.org', 'connect@myapp.org']
    elif app == 'CS':
        if env == 'Test':
            return ['https://cs-testing-api.myapp.org', 'https://cs-myapp-testing.myapp.org/admin',
                    'cs.customersupport@myapp.org']
        elif env == 'Staging':
            return ['https://cs-staging-api.myapp.org', 'https://cs-myapp-staging.myapp.org/admin',
                    'cs.customersupport@myapp.org']
        elif env == 'Production':
            return ['https://cs-api.myapp.org', 'https://credit-suisse.myapp.org/admin',
                    'cs.customersupport@myapp.org']
        else:
            return ['https://dev-api.myapp.org', 'https://myapp-dev.myapp.org', 'connect@myapp.org']
    else:
        return ['https://dev-api.myapp.org', 'https://myapp-dev.myapp.org', 'connect@myapp.org']


def fetch_api_config(username):
    if username.lower().startswith('cnp'):
        return api_conf('myapp_cs', find_host('CS', os.getenv('ENV')))
    else:
        return api_conf('myapp', find_host('ML', os.getenv('ENV')))
