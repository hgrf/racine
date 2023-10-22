import base64
import json

from flask_mail import Mail
from flask import current_app as app

from .settings.forms import EmailSettings


def send_mail(to: list[str], subject: str, **kwargs) -> None:
    """
    Send a mail using the current app configuration.

    Examples::

        >>> send_mail(["john.doe@gmail.com"], "Hello", body="Hello, John!")

    Arguments:
        to -- List of recipients.
        subject -- Subject of the email.
        **kwargs -- Additional arguments to be passed to flask_mail.Mail.send_message.
    """
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


def read_mailconfig(form: EmailSettings):
    # load email settings
    with open("data/mailconfig.json") as f:
        mailconfig = json.load(f)
        form.sender.data = mailconfig["MAIL_SENDER"]
        form.server.data = mailconfig["MAIL_SERVER"]
        form.port.data = mailconfig["MAIL_PORT"]
        form.use_ssl.data = mailconfig["MAIL_USE_SSL"]
        form.use_tls.data = mailconfig["MAIL_USE_TLS"]
        form.username.data = mailconfig["MAIL_USERNAME"]


def write_mailconfig(form: EmailSettings):
    with open("data/mailconfig.json", "w") as f:
        json.dump(
            {
                "MAIL_SENDER": form.sender.data,
                "MAIL_SERVER": form.server.data,
                "MAIL_PORT": form.port.data,
                "MAIL_USE_SSL": form.use_ssl.data,
                "MAIL_USE_TLS": form.use_tls.data,
                "MAIL_USERNAME": form.username.data,
                "MAIL_PASSWORD": base64.b64encode(form.password.data.encode("utf8")).decode("utf8"),
            },
            f,
        )
