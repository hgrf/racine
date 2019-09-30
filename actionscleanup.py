"""
    This script is meant to clean up the actions table in the database in order to remove two "relics" of the first
    Sample Manager versions:
    - complete HTML documents in the action description, leading to an override of the app's font with Ubuntu font
    - missing action timestamps, leading to the display of the corresponding samples on the print page even when not
      supposed to
"""

import os
import datetime
from app import create_app, db
from app.models import Action

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()        # https://stackoverflow.com/a/19438054

actions = Action.query.all()

for a in actions:
    if "<!DOCTYPE" in a.description:
        print "Found HTML issue in action", a.id, "from sample", a.sample.id, ":", a.sample.name
        new_description = ''
        paragraph_start = -1
        while True:
            paragraph_start = a.description.find('<p', paragraph_start+1)
            paragraph_start_endtag = a.description.find('>', paragraph_start)
            if paragraph_start < 0:
                break
            paragraph_end = a.description.find('</p>', paragraph_start)
            print "Identified paragraph:", a.description[paragraph_start_endtag+1:paragraph_end]
            new_description += "<p>"+a.description[paragraph_start_endtag+1:paragraph_end]+"</p>"

        print "Please confirm correction of action description:"
        print "OLD:\n================================"
        print a.description
        print "NEW:\n================================"
        print new_description
        raw_input("Press Enter to confirm or CTRL+C to cancel")
        a.description = new_description
        db.session.commit()

    if a.timestamp is None:
        print "Found timestamp issue in action", a.id, "from sample", a.sample.id, ":", a.sample.name
        print "The timestamp will be set to 2015-01-01 and a corresponding note will be added to the description"
        raw_input("Press Enter to confirm or CTRL+C to cancel")
        a.timestamp = datetime.datetime.strptime("2015-01-01", '%Y-%m-%d')
        a.description = "<p>AD HOC TIMESTAMP 2015-01-01</p>"+a.description
        db.session.commit()
