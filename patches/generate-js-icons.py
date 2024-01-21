import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.common import icons_dict  # noqa: E402

with open("js/src/util/icons.js", "w") as f:
    f.write("const icons = {};\n".format(json.dumps(icons_dict, indent=4)))
    f.write("export default icons;\n")
