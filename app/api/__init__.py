from flask import Blueprint

api = Blueprint("api", __name__)

from app.api import (  # noqa: E402
    actions,
    emailing,
    fields,
    samples,
    shares,
)


class APIModule:
    def __init__(self, name, module, description):
        self.name = name
        self.module = module
        self.description = description


modules = [
    APIModule("samples", samples, "Endpoints related to samples"),
    APIModule("shares", shares, "Endpoints related to shares"),
    APIModule("actions", actions, "Endpoints related to actions"),
    APIModule("emailing", emailing, "Endpoints related to emailing"),
    APIModule("fields", fields, "Endpoints related to fields"),
]
