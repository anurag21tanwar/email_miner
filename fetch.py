import imaplib
from config.config import mail_conf
from utils.mail import fetch_mail_metadata
import time
import traceback


while True:
    m = imaplib.IMAP4_SSL(mail_conf['server'])
    m.login(mail_conf['email'], mail_conf['password'])
    m.select('inbox')

    try:
        code, data = m.search(None, '(UNSEEN)')

        print('==CHECKING FOR NEW MESSAGES==')

        if code == 'OK':
            for num in data[0].split():
                typ, data = m.fetch(num, '(RFC822)')
                for res in data:
                    fetch_mail_metadata(m, num, res)

            time.sleep(10)

    except Exception:
        print(traceback.print_exc())
    finally:
        m.close()
        m.logout()
        time.sleep(60)
