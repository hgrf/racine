from flask import jsonify, request
from marshmallow import fields
from sqlalchemy import not_

from . import api
from .common import OrderedSchema
from .errors import bad_request
from ..settings.forms import NewUserForm

from ..common import db
from ..models import Sample, Share, User, record_activity, token_auth
from ..models.user import current_user


class ModeParameter(OrderedSchema):
    mode = fields.Str(metadata={"description": '"share", "leave" or anything else (default)'})
    sampleid = fields.Int(metadata={"description": 'sample ID (only for mode="share")'})


class UserListSchema(OrderedSchema):
    users = fields.List(fields.Str(), metadata={"description": "list of users according to mode"})
    recent = fields.List(
        fields.Str(), metadata={"description": 'list of recently shared with users (mode="share")'}
    )


class NewUserFormContent(OrderedSchema):
    csrf_token = fields.Str(metadata={"description": "CSRF (Cross Site Request Forgery) token"})
    is_admin = fields.Bool(metadata={"description": "whether the user is an administrator"})
    username = fields.Str(metadata={"description": "username of the new user"})
    email = fields.Str(metadata={"description": "email address of the new user"})
    password = fields.Str(metadata={"description": "password of the new user"})
    password2 = fields.Str(metadata={"description": "password confirmation of the new user"})


@api.route("/user", methods=["PUT"])
@token_auth.login_required
def createuser():
    """Create a user in the database.
    ---
    put:
      operationId: createUser
      description: Create a user in the database.
      tags: [users]
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: NewUserFormContent
      responses:
        201:
          description: User created
    """
    if not current_user().is_admin:
        return bad_request("Invalid request.")
    form = NewUserForm()
    if form.validate_on_submit():
        try:
            user = User(
                is_admin=form.is_admin.data,
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
            )
            db.session.add(user)
            db.session.commit()
            record_activity("add:user", token_auth.current_user(), commit=True)
            return "", 201
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"email": [str(e)]}), 400
    elif form.is_submitted():
        error = {field: errors for field, errors in form.errors.items()}
        return jsonify(error=error), 400

    return "", 500  # this should never happen


@api.route("/user/<int:userid>", methods=["DELETE"])
@token_auth.login_required
def deleteuser(userid):
    """Delete a user from the database.
    ---
    delete:
      operationId: deleteUser
      description: Delete a user from the database.
      tags: [users]
      parameters:
      - in: path
        name: userid
        schema:
          type: integer
        required: true
        description: Numeric ID of the user to delete.
      responses:
        204:
          description: User deleted
    """
    user = User.query.get(userid)
    db.session.delete(user)
    record_activity("delete:user", token_auth.current_user())
    db.session.commit()
    return "", 204


@api.route("/users", methods=["POST"])
@token_auth.login_required
def userlist():
    """Get a list of users from the database, according to one of three modes.
    ---
    post:
      operationId: getUserList
      description: |
        Get a list of users from the database, according to one of three modes.

        The modes are:

        * "share":  Used by the "UserBrowser" dialog when sharing a sample. Returns a list of users
                    that are not the current user and that do not already share the sample and a
                    list of users that the current user has recently shared with.
        * "leave":  Used by the "username" field on the leave page. Returns a list of users that are
                    not the current user and that do not have an heir.
        * default:  Returns all users.
      tags: [users]
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: ModeParameter
      responses:
        200:
          content:
            application/json:
              schema: UserListSchema
          description: List of users according to mode (see above)
    """
    # get list of all users
    users = User.query.all()

    # determine mode
    mode = request.form.get("mode")
    if mode == "share":
        # get list of people who already share this sample
        sample = Sample.query.get(int(request.form.get("sampleid")))
        sharers = [share.user for share in sample.shares]
        sharers.append(sample.owner)

        # get list of max. 5 people that the current user has recently shared with
        list1 = [
            {"id": share.id, "name": share.user.username}
            for share in Share.query.outerjoin(Sample, Sample.id == Share.sample_id)
            .filter(Sample.owner_id == current_user().id)
            .filter(not_(Share.user_id.in_([x.id for x in sharers])))
            .order_by(Share.id.desc())
            .group_by(Share.user_id)
            .limit(5)
            .all()
        ]

        # get list of max. 5 people that have recently shared with current user
        list2 = [
            {"id": share.id, "name": share.sample.owner.username}
            for share in Share.query.filter(Share.user_id == current_user().id)
            .outerjoin(Sample, Sample.id == Share.sample_id)
            .filter(not_(Sample.owner_id.in_([x.id for x in sharers])))
            .order_by(Share.id.desc())
            .group_by(Sample.owner_id)
            .limit(5)
            .all()
        ]

        # now combine them, order by descending ID, remove duplicates and truncate to 5 elements
        list = sorted(list1 + list2, key=lambda x: x["id"], reverse=True)
        finallist = []
        for i, x in enumerate(list):
            if len(finallist) > 4:
                break
            if x["name"] not in finallist:
                finallist.append(x["name"])

        return jsonify(
            users=[user.username for user in users if user not in sharers], recent=finallist
        )
    elif mode == "leave":
        return jsonify(
            users=[user.username for user in users if user != current_user() and user.heir is None]
        )
    else:
        return jsonify(users=[user.username for user in users])
