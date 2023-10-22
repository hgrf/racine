import base64
import json

from flask_mail import Mail
from flask import current_app as app


def send_mail(to, subject, **kwargs):
    # load email settings and update app config dynamically
    with open("data/mailconfig.json") as f:
        mailconfig = json.load(f)
    mailconfig["MAIL_PASSWORD"] = base64.b64decode(
        mailconfig["MAIL_PASSWORD"].encode("utf8")
    ).decode("utf8")
    app.config.update(mailconfig)

    # send email
    mail = Mail(app)
    mail.send_message(
        subject, sender=("Racine Admin", app.config["MAIL_SENDER"]), recipients=to, **kwargs
    )


def read_mailconfig():
    # load email settings
    with open("data/mailconfig.json") as f:
        mailconfig = json.load(f)
    return mailconfig
