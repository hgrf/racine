import os
import ctypes
import platform
from sqlalchemy.sql import func
from . import db
from .models import Upload


# from https://stackoverflow.com/a/2372171
def get_free_space(dirname):
    """Return folder/drive free space."""
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(dirname)
        return st.f_bavail * st.f_frsize


def filesystem_usage(app):
    with app.app_context():
        # get size of the SQLite database
        dbsize = os.path.getsize(app.config['SQLALCHEMY_DATABASE_URI'][10:])

        # get total upload volume (code redundant with main/views.py)
        totuploadvol = db.session.query(func.sum(Upload.size)).first()[0]

        # get free disk space (code redundant with main/views.py)
        availablevol = get_free_space(os.path.dirname(__file__))
    return dbsize, totuploadvol, availablevol
