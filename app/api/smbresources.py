from flask import jsonify
from marshmallow import fields

from . import api
from .common import OrderedSchema
from .errors import bad_request
from ..settings.forms import NewSMBResourceForm

from ..common import db
from ..models import SMBResource, record_activity, token_auth
from ..models.user import current_user


class NewSMBResourceFormContent(OrderedSchema):
    csrf_token = fields.Str(metadata={"description": "CSRF (Cross Site Request Forgery) token"})
    name = fields.Str(metadata={"description": "name of the SMB resource"})
    servername = fields.Str(metadata={"description": "NetBIOS name of the SMB server"})
    serveraddr = fields.Str(metadata={"description": "IP address or hostname of the SMB server"})
    serverport = fields.Str(metadata={"description": "TCP port of the SMB server"})
    domainname = fields.Str(metadata={"description": "domain name of the SMB server"})
    sharename = fields.Str(metadata={"description": "share name on the SMB server"})
    path = fields.Str(metadata={"description": "path to the desired resource on the SMB server"})
    userid = fields.Str(metadata={"description": "user ID for authentication on the SMB server"})
    password = fields.Str(metadata={"description": "password for authentication on the SMB server"})


@api.route("/smbresource", methods=["PUT"])
@token_auth.login_required
def createsmbresource():
    """Create a SMB resource in the database.
    ---
    put:
      operationId: createSMBResource
      description: Create a SMB resource in the database.
      tags: [smbresources]
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: NewSMBResourceFormContent
      responses:
        201:
          description: SMB resource created
    """
    if not current_user().is_admin:
        return bad_request("Invalid request.")
    form = NewSMBResourceForm()
    if form.validate_on_submit():
        try:
            smbresource = SMBResource(
                name=form.name.data,
                servername=form.servername.data,
                serveraddr=form.serveraddr.data,
                serverport=form.serverport.data,
                domainname=form.domainname.data,
                sharename=form.sharename.data,
                path=form.path.data,
                userid=form.userid.data,
                password=form.password.data,
            )
            db.session.add(smbresource)
            db.session.commit()
            record_activity("add:smbresource", token_auth.current_user(), commit=True)
            return "", 201
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"name": [str(e)]}), 400
    elif form.is_submitted():
        error = {field: errors for field, errors in form.errors.items()}
        return jsonify(error=error), 400

    return "", 500  # this should never happen


@api.route("/smbresource/<int:resourceid>", methods=["DELETE"])
@token_auth.login_required
def deletesmbresource(resourceid):
    """Delete a SMB resource from the database.
    ---
    delete:
      operationId: deleteSMBResource
      description: Delete a SMB resource from the database.
      tags: [smbresources]
      parameters:
      - in: path
        name: resourceid
        schema:
          type: integer
        required: true
        description: Numeric ID of the SMB resource to delete.
      responses:
        204:
          description: SMB resource deleted
    """
    resource = SMBResource.query.get(resourceid)
    db.session.delete(resource)
    record_activity("delete:smbresource", token_auth.current_user())
    db.session.commit()
    return "", 204
