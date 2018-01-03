from flask_mail import Mail, Message
from flask import current_app as app
import ast

def send_mail(to, subject, **kwargs):
    # load email settings and update app config dynamically
    with open('mailconfig.py') as f:
        mailconfig = f.read()
        mailconfig = ast.literal_eval(mailconfig)
    app.config.update(mailconfig)

    # send email
    mail = Mail(app)
    msg = mail.send_message(
        subject,
        sender=('MSM Admin', app.config['MAIL_SENDER']),
        recipients=to,
        **kwargs
    )

def read_mailconfig():
    # load email settings
    with open('mailconfig.py') as f:
        mailconfig = f.read()
        mailconfig = ast.literal_eval(mailconfig)
    return mailconfig