import os
import time
import git
import requests
import uuid
import threading
from config import basedir
from . import db
from .models import User, Sample, Action, Upload
from sqlalchemy.sql import func

start_time = time.time()
usage_statistics_url_source = 'https://raw.githubusercontent.com/HolgerGraef/MSM-usage-statistics/master/url'
usage_statistics_sleep_time = 60.       # wait 1 minute after every update

# read site name from file if possible
if os.path.exists('usage_stats_site'):
    with open('usage_stats_site', 'r') as f:
        usage_statistics_site_name = f.readline().strip()
else:
    usage_statistics_site_name = 'unknown'


class UsageStatisticsThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.daemon = True  # kill the thread when the app is killed

        # run usage statistics thread (only run once, even in debug mode)
        if (not app.debug) or (os.environ.get("WERKZEUG_RUN_MAIN") == 'true'):
            self.start()

    def run(self):
        # determine site key or create one
        if os.path.exists('usage_stats_key'):
            with open('usage_stats_key', 'r') as f:
                key = f.readline().strip()
        else:
            key = str(uuid.uuid4())
            with open('usage_stats_key', 'w') as f:
                f.write(key)

        # obtain git revision and check if repo is clean
        repo = git.Repo(basedir)  # get Sample Manager git repo
        git_rev = str(repo.rev_parse('HEAD'))
        git_clean = str(not repo.is_dirty())

        totuploadvol, availablevol = filesystem_usage(self.app)

        while True:
            with self.app.app_context():
                data = {'key': key,
                        'site': usage_statistics_site_name,
                        'users': User.query.count(),
                        'samples': Sample.query.count(),
                        'actions': Action.query.count(),
                        'starttime': start_time,
                        'uptime': time.time()-start_time,
                        'gitrev': git_rev,
                        'gitclean': git_clean,
                        'uploadvol': totuploadvol,
                        'availablevol': availablevol}

            # get usage statistics script url from GitHub
            try:
                response = requests.get(usage_statistics_url_source)
                if response.status_code == 200:
                    url = response.content.strip()
                    requests.post(url, json=data)
            except Exception as e:
                pass        # do not crash when there is e.g. a ConnectionError, simply keep trying

            time.sleep(usage_statistics_sleep_time)


def filesystem_usage(app):
    with app.app_context():
        # get total upload volume (code redundant with main/views.py)
        stmt = db.session.query(Upload.user_id, func.sum(Upload.size).label('upload_volume')).group_by(Upload.user_id).subquery()
        uploadvols = db.session.query(User, stmt.c.upload_volume).outerjoin(stmt, User.id == stmt.c.user_id).order_by(User.id).all()
        totuploadvol = 0
        for u in uploadvols:
            totuploadvol += u[1] if u[1] is not None else 0

        # get free disk space (code redundant with main/views.py)
        statvfs = os.statvfs(os.path.dirname(__file__))
        availablevol = statvfs.f_frsize * statvfs.f_bavail
    return totuploadvol, availablevol
