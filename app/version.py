import os


with open(os.path.join(os.path.dirname(__file__), "..", "version.csv"), "r") as f:
    RACINE_VERSION = None
    RACINE_API_VERSION = None
    for line in f:
        key, val = line.split(",", 1)
        if key == "RACINE_VERSION":
            RACINE_VERSION = val.strip()
        elif key == "RACINE_API_VERSION":
            RACINE_API_VERSION = val.strip()

    if RACINE_VERSION is None or RACINE_API_VERSION is None:
        raise Exception("version.csv is missing RACINE_VERSION or RACINE_API_VERSION")
