# see also:
# https://github.com/ciscomonkey/flask-pyinstaller
# https://elc.github.io/posts/executable-flask-pyinstaller/
# https://github.com/smoqadam/PyFladesk

# TODO:
#  - figure out why disk usage is full in standalone .exe
#  - reduce executable folder size by removing unnecessary libraries

from app import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from pyfladesk import init_gui

app = create_app('standalone')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def gui():
    init_gui(app, width=1024, height=768, window_title="Mercury Sample Manager", icon="app/static/images/sample.png")


if __name__ == '__main__':
    manager.run(default_command='gui')
