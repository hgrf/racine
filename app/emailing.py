from flask_mail import Mail
from flask import current_app as app
import ast
import base64


def send_mail(to, subject, **kwargs):
    # load email settings and update app config dynamically
    with open("mailconfig.py") as f:
        mailconfig = f.read()
        mailconfig = ast.literal_eval(mailconfig)
    mailconfig["MAIL_PASSWORD"] = base64.b64decode(
        mailconfig["MAIL_PASSWORD"].encode("utf8")
    ).decode("utf8")
    app.config.update(mailconfig)

    # send email
    mail = Mail(app)
    msg = mail.send_message(
        subject, sender=("Racine Admin", app.config["MAIL_SENDER"]), recipients=to, **kwargs
    )


def read_mailconfig():
    # load email settings
    with open("mailconfig.py") as f:
        mailconfig = f.read()
        mailconfig = ast.literal_eval(mailconfig)
    return mailconfig
