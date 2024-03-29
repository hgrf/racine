import json
import os
import time
import requests
import uuid
import psutil
from celery.utils.log import get_task_logger
from flask import current_app
from sqlalchemy.sql import func

from .abstract.async_task import shared_task
from .abstract.kv_store import kvs_set
from .common import db
from .version import RACINE_VERSION
from .models import User, Sample, Action, Upload

logger = get_task_logger(__name__)
start_time = time.time()
usage_statistics_url_source = (
    "https://raw.githubusercontent.com/hgrf/MSM-usage-statistics/master/url"
)


@shared_task(name="usage_stats_task")
def usage_stats_task():
    # determine site key or create one
    if os.path.exists("data/usage_stats_key"):
        with open("data/usage_stats_key", "r") as f:
            key = f.readline().strip()
    else:
        key = str(uuid.uuid4())
        with open("data/usage_stats_key", "w") as f:
            f.write(key)

    # read site name from file if possible
    if os.path.exists("data/usage_stats_site"):
        with open("data/usage_stats_site", "r") as f:
            usage_statistics_site_name = f.readline().strip()
    else:
        usage_statistics_site_name = "unknown"

    # obtain file system usage
    dbsize, totuploadvol, availablevol = filesystem_usage()

    # obtain RAM usage
    ram_used = psutil.virtual_memory().used

    action_count = Action.query.join(Sample).filter(Sample.isdeleted == False).count()  # noqa: E712

    data = {
        "key": key,
        "site": usage_statistics_site_name,
        "version": RACINE_VERSION,
        "users": User.query.count(),
        "samples": Sample.query.filter_by(isdeleted=False).count(),
        "actions": action_count,
        "starttime": start_time,
        "uptime": time.time() - start_time,
        "dbsize": dbsize,
        "uploadvol": totuploadvol,
        "availablevol": availablevol,
        "ramused": ram_used,
    }

    # publish data to key-value-store
    kvs_set("usage-stats", json.dumps(data, indent=4))

    # get usage statistics script url from GitHub
    try:
        response = requests.get(usage_statistics_url_source, timeout=5)
        if response.status_code == 200:
            url = response.content.strip()
            logger.info("Submitting data with {} to {}: {}".format(key, url, data))
            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                logger.info("Usage statistics data submitted successfully")
            else:
                logger.error("Could not submit usage statistics data")
        else:
            logger.error("Could not get usage statistics endpoint URL from GitHub")
    except Exception:
        pass  # do not crash when there is e.g. a ConnectionError, simply keep trying


def filesystem_usage():
    # get size of the SQLite database
    dbsize = 0
    dbsize = os.path.getsize(current_app.config["SQLALCHEMY_DATABASE_URI"][10:])

    # get total upload volume (code redundant with main/views.py)
    totuploadvol = db.session.query(func.sum(Upload.size)).first()[0]

    # get free disk space (code redundant with main/views.py)
    statvfs = os.statvfs(os.path.dirname(__file__))
    availablevol = statvfs.f_frsize * statvfs.f_bavail

    return dbsize, totuploadvol, availablevol
