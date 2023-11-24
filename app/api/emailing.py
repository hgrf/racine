import base64
import json

from celery import shared_task, current_task
from flask import current_app as app
from flask import jsonify
from flask_mail import Mail
from marshmallow import fields

from . import api
from .common import OrderedSchema
from ..models import token_auth


class MailProgressRequest(OrderedSchema):
    task_id = fields.Str()


class MailProgressResponse(OrderedSchema):
    state = fields.Str()
    current = fields.Int()
    total = fields.Int()
    status = fields.Str()
    result = fields.Str()


@shared_task(name="send_mail_task", soft_time_limit=10)
def send_mail_task(to: list[str], subject: str, **kwargs):
    current_task.update_state(state="RUNNING", meta={"status": "Sending email..."})
    try:
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
    except Exception as e:
        current_task.update_state(
            state="FAILURE",
            meta={"exc_type": type(e).__name__, "exc_message": "Failed to send email: " + str(e)},
        )
        return

    current_task.update_state(state="SUCCESS", meta={"status": "Email sent successfully"})


@api.route("/send_mail_progress/<task_id>", methods=["GET"])
@token_auth.login_required
def send_mail_progress(task_id: str):
    """Get field value of a database item.
    ---
    get:
      operationId: getMailProgress
      parameters:
      - in: path
        schema: MailProgressRequest
      responses:
        200:
          content:
            application/json:
              schema: MailProgressResponse
          description: Field value fetched successfully
    """
    task = send_mail_task.AsyncResult(task_id)
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "current": 0,
            "total": 1,
            "status": "Pending...",
        }
    elif task.state != "FAILURE":
        response = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": task.info.get("total", 1),
            "status": task.info.get("status", ""),
        }
        if "result" in task.info:
            response["result"] = task.info["result"]
    else:
        response = {
            "state": task.state,
            "current": 1,
            "total": 1,
            "status": str(task.info),  # this is the exception raised
        }
    return jsonify(response)
