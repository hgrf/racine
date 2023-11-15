import json
import os
import time
import redis
import requests
import uuid
import psutil
from celery import shared_task
from celery.utils.log import get_task_logger
from flask import current_app
from sqlalchemy.sql import func

from . import db, RACINE_VERSION
from .models import User, Sample, Action, Upload

logger = get_task_logger(__name__)
start_time = time.time()
usage_statistics_url_source = (
    "https://raw.githubusercontent.com/hgrf/MSM-usage-statistics/master/url"
)


@shared_task(name="usage_stats_task")
def periodic_task():
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

    data = {
        "key": key,
        "site": usage_statistics_site_name,
        "version": RACINE_VERSION,
        "users": User.query.count(),
        "samples": Sample.query.filter_by(isdeleted=False).count(),
        "actions": Action.query.join(Sample).filter(not Sample.isdeleted).count(),
        "starttime": start_time,
        "uptime": time.time() - start_time,
        "dbsize": dbsize,
        "uploadvol": totuploadvol,
        "availablevol": availablevol,
        "ramused": ram_used,
    }

    # publish data to redis
    r = redis.Redis(host="racine-redis", port=6379, decode_responses=True)
    r.set("usage-stats", json.dumps(data, indent=4))

    # get usage statistics script url from GitHub
    try:
        response = requests.get(usage_statistics_url_source)
        if response.status_code == 200:
            url = response.content.strip()
            logger.info("Submitting data with {} to {}: {}".format(key, url, data))
            requests.post(url, json=data)
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
