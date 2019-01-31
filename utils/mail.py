import mailparser
import traceback
from utils.error import fetch_error_handler
from utils.db import create_email_record, create_file_record, save_email_password


def extract_password(body):
    tmp = []
    pass_ = body.split('On')[0].strip()
    for p in pass_.split('\n'):
        if p:
            tmp.append(p.strip())
    return tmp


def extract_username(addr):
    tmp = addr.split('@')[0]
    if tmp.find('<') == -1:
        return tmp
    else:
        return tmp.split('<')[1]


def extract_subject(sub):
    if sub.find(':') == -1:
        return sub.strip()
    else:
        return sub.split(':')[1].strip()


def fetch_mail_metadata(m, num, res):
    if isinstance(res, tuple):
        try:
            mail = mailparser.parse_from_bytes(res[1])

            subject = mail.subject.strip()
            mailfrom = mail.from_[0][1]
            mailto = mail.to[0][1]
            body = mail.body
            attachments = mail.attachments
            date = mail.date
            messageid = mail.message_id
            # username = extract_username(mailfrom)  # TODO: remove this line before deploying
            username = extract_username(mailto)

            if mailto.find('@myapp.org') != -1 and username != 'anonymizer' and subject:
                print('==FOUND==')

                if len(attachments) > 0:
                    create_email_record({'subject': subject, 'mail_from': mailfrom, 'mail_to': mailto,
                                         'username': username, 'received_at': str(date), 'message_id': messageid})

                    for attachment in attachments:
                        create_file_record({'username': username, 'message_id': messageid, 'date': date,
                                            'attachment': attachment})

                else:
                    pass_ = extract_password(body)
                    sub_ = extract_subject(subject)

                    save_email_password({'username': username, 'subject': sub_, 'passwords': pass_})
            else:
                print('invalid mailto/username/subject', mailto, username, subject)
        except Exception as e:
            print(traceback.print_exc())
            fetch_error_handler(m, num, e)
        finally:
            m.store(num, '+FLAGS', '\\SEEN')
