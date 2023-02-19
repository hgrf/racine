# credit to https://stackoverflow.com/a/62166840

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import create_app, api
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

import json


spec = APISpec(
    title="MSM API",
    version="0.1.0-dev",
    openapi_version="3.0.2",
    info=dict(
        description="MSM API",
        version="0.1.0-dev",
        contact=dict(
            email="holger.graef@gmail.com",
        ),
        license=dict(
            name="GPL v3", url="https://github.com/HolgerGraef/MSM/blob/master/LICENSE.md"
        ),
    ),
    tags=[dict(name="MSM", description="Endpoints related to MSM")],
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

app = create_app("testing")
with app.test_request_context():
    spec.path(view=api.samples.deletesample)

    spec.path(view=api.shares.deleteshare)

    spec.path(view=api.actions.createaction)
    spec.path(view=api.actions.deleteaction)

with open("swagger.json", "w") as f:
    json.dump(spec.to_dict(), f, indent=4)

with open("api.yaml", "w") as f:
    f.write(spec.to_yaml())
