import inspect

from datetime import datetime
from flask import jsonify, request
from marshmallow import fields, validate

from . import api
from .common import OrderedSchema
from .errors import bad_request

from .. import db
from ..models import Action, Sample, Share, SMBResource, User, record_activity, token_auth
from ..models.user import current_user
from ..validators import validate_form_field

from ..main.forms import NewSampleForm
from ..settings.forms import NewUserForm


def str_to_bool(str):
    if str.lower() == "true" or str == "1":
        return True
    elif str.lower() == "false" or str == "0":
        return False
    else:
        raise Exception("String could not be converted to boolean")


def validate_is_admin(str, item):
    b = str_to_bool(str)
    if item.is_admin and not b:
        # check if any other administrators are left
        if len(User.query.filter_by(is_admin=True).all()) == 1:
            raise Exception("There has to be at least one administrator.")
    return b


# define supported fields
supported_targets = {
    "sample": {
        "dbobject": Sample,
        "auth": "owner",
        "fields": {
            "name": lambda x: validate_form_field(NewSampleForm(), "name", x),
            "description": str,
            "image": str,
        },
    },
    "action": {
        "dbobject": Action,
        "auth": "action_auth",
        "fields": {"timestamp": lambda x: datetime.strptime(x, "%Y-%m-%d"), "description": str},
    },
    "share": {"dbobject": Share, "auth": None, "fields": {}},
    "smbresource": {
        "dbobject": SMBResource,
        "auth": "admin",
        "fields": {
            "name": str,
            "servername": str,
            "serveraddr": str,
            "serverport": int,
            "domainname": str,
            "sharename": str,
            "path": str,
            "userid": str,
            "password": str,
        },
    },
    "user": {
        "dbobject": User,
        "auth": "admin",
        "fields": {
            "username": lambda x: validate_form_field(NewUserForm(), "username", x),
            "email": lambda x: validate_form_field(NewUserForm(), "email", x),
            "is_admin": validate_is_admin,
        },
    },
}


class FieldParameters(OrderedSchema):
    target = fields.Str(validate=validate.OneOf(supported_targets.keys()))
    id = fields.Int()
    # TODO: add target-specific field validation
    field = fields.Str()


class ValueSchema(OrderedSchema):
    value = fields.Str()


# TODO: both getfield and setfield should check if the sample is marked as deleted


@api.route("/get/<target>/<field>/<int:id>", methods=["GET"])
@token_auth.login_required
def getfield(target, field, id):
    """Get field value of a database item.
    ---
    get:
      operationId: getField
      tags: [fields]
      parameters:
      - in: path
        schema: FieldParameters
      responses:
        200:
          content:
            application/json:
              schema: ValueSchema
          description: Field value fetched successfully
    """
    if not (id and target and field and target in supported_targets):
        return bad_request("Invalid request.")

    # redefine target to simplify
    target = supported_targets[target]

    # try to get requested item from database
    item = target["dbobject"].query.get(id)

    # check if the item is valid and if the requested field is supported
    if not (item and field in target["fields"]):
        return bad_request("Invalid request.")

    # check if the current user is authorized to access this item
    if (
        not (target["auth"] == "owner" and item.owner == current_user())
        and not (target["auth"] == "admin" and current_user().is_admin)
        and not (target["auth"] == "action_auth" and item.has_read_access(current_user()))
    ):
        return bad_request("Invalid request.")

    # return value
    return jsonify(value=getattr(item, field)), 200


@api.route("/set/<target>/<field>/<int:id>", methods=["POST"])
@token_auth.login_required
def updatefield(target, field, id):
    """Set field value of a database item.
    ---
    post:
      operationId: setField
      tags: [fields]
      parameters:
      - in: path
        schema: FieldParameters
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: ValueSchema
      responses:
        200:
          content:
            application/json:
              schema: EmptySchema
          description: Field value updated successfully
    """
    if not (id and target and field and target in supported_targets):
        return bad_request("Invalid request.")

    value = request.form.get("value")

    # redefine target to simplify
    target_name = target
    target = supported_targets[target]

    # try to get requested item from database
    item = target["dbobject"].query.get(id)

    # check if the item is valid and if the requested field is supported
    if not (item and field in target["fields"]):
        return bad_request("Invalid request.")

    # check if the current user is authorized to access this item
    if (
        not (target["auth"] == "owner" and item.owner == current_user())
        and not (target["auth"] == "admin" and current_user().is_admin)
        and not (target["auth"] == "action_auth" and item.has_write_access(current_user()))
    ):
        return bad_request("Invalid request.")

    # try to assign value
    try:
        # check if a modifier is to be applied
        modifier = target["fields"][field]
        if modifier is None:
            setvalue = value
        # check if the modifier is a function
        elif type(modifier) == type(lambda x: x):
            argno = len(inspect.getargspec(modifier).args)
            if argno == 1:
                setvalue = modifier(value)
            elif argno == 2:
                setvalue = modifier(value, item)
            elif argno == 3:
                setvalue = modifier(value, item, field)
            else:
                raise Exception("Invalid modifier")
        # otherwise it is probably simply type casting
        else:
            setvalue = modifier(value)
        if getattr(item, field) != setvalue:
            setattr(item, field, setvalue)
            if target_name == "sample":
                sample = item
            elif target_name == "action":
                sample = item.sample
            else:
                sample = None
            record_activity("update:" + target_name + ":" + field, current_user(), sample)

    except Exception as e:
        return jsonify(value=str(getattr(item, field)), message="Error: " + str(e)), 400

    # commit changes to database
    db.session.commit()
    return jsonify(value=value), 200
