# credit to https://stackoverflow.com/a/62166840

import json
import os
import sys

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import create_app, api  # noqa: E402
from app.version import RACINE_API_VERSION  # noqa: E402


spec = APISpec(
    title="Racine API",
    version=RACINE_API_VERSION,
    openapi_version="3.0.2",
    info=dict(
        description="Racine API",
        version=RACINE_API_VERSION,
        contact=dict(
            email="holger.graef@gmail.com",
        ),
        license=dict(name="GPL v3", url="https://github.com/hgrf/racine/blob/master/LICENSE.md"),
    ),
    tags=[dict(name=m.name, description=m.description) for m in api.modules],
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
    security=[{"bearerAuth": []}],
)

app = create_app("testing")
with app.test_request_context():
    spec.components.security_scheme(
        "bearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )

    for m in api.modules:
        for name, attr in m.module.__dict__.items():
            if callable(attr):
                if hasattr(attr, "__doc__") and "operationId:" in str(attr.__doc__):
                    spec.path(view=attr)

with open("docs/swagger.json", "w") as f:
    json.dump(spec.to_dict(), f, indent=4)

with open("docs/api.yaml", "w") as f:
    f.write(spec.to_yaml())
