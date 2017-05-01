import os
from app import create_app, db
from flask.ext.script import Manager
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker, make_transient
from shutil import copyfile

from app.models import Sample, User, SampleType, ActionType, Upload, Action

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                          'sqlite:///' + os.path.join(basedir, 'database/data-dev.sqlite')

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

# Connect to import database
sqlite_url = 'sqlite:///' + os.path.join(basedir, 'import/database/data.sqlite')
engine = create_engine(sqlite_url)
# initialize the db if it hasn't yet been initialized
db.metadata.create_all(engine)
Session = sessionmaker(engine)
src_sess = Session()  # import (source) database session
dst_sess = db.session  # main (destination) database session


# TO ACCESS THE IMPORT DATABASE:
#    print src_session.query(Sample).all()
#
# TO ACCESS THE MAIN DATABASE:
#    print dst_session.query(Sample).all()

@manager.command
def execute():
    class color:
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        DARKCYAN = '\033[36m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

    def match(table, column, description=None):
        print color.BOLD+"Looking for matching", (description if description is not None else "item")+"s"+color.END
        matched = []
        dest_items = dst_sess.query(table).all()
        for item1 in src_sess.query(table).all():
            if getattr(item1, column) is None:
                print "Ignoring", description if description is not None else "item","with ID: ", item1.id, " because the relevant field is None."
                continue
            for item2 in dest_items:
                if getattr(item1, column) == getattr(item2, column):
                    print "Match found: ", getattr(item1, column)
                    matched.append((item1.id, item2.id))
                    dest_items.remove(item2)
        return matched

    def simple_import(table, matched, description=None):
        for item in src_sess.query(table).all():
            if item.id not in [x[0] for x in matched]:
                print "Importing unmatched", (description if description is not None else "item")+":", item
                old_id = item.id
                src_sess.expunge(item)
                make_transient(item)
                item.id = None
                dst_sess.add(item)
                dst_sess.commit()
                matched.append((old_id, item.id))

    # I know, I'm reinventing the dictionary....
    def lookup(matched, id):
        result = None
        for match in matched:
            if id == match[0]:
                result = match[1]
                break
        if result is None:
            print "Could not find match for id ", id
        return result

    def update_html(text, itemid, matched_uploads, matched_samples):
        i = -1
        while True:
            i = text.find('<img', i + 1)
            if i != -1:
                j = text.find('>', i)  # end of a tag
                k = text.find('src=', i)
                assert k < j  # make sure the href attr. belongs to the a tag
                l = k + 4
                invcomma = text[l]
                m = text.find(invcomma, l + 1)
                assert m < j  # make sure the string ends before the end of the a tag

                img_src = text[l+1:m]
                if not "/browser/ulimg/" in img_src: # this will also be true for ERRONEOUS references of the type "https://localhost/browser/ulimg..."
                    print "unchanged img tag: \"{}\"".format(img_src)
                    continue
                toks = img_src.split('/') # toks[-1] will be the reference to the upload
                new_img_src = "/browser/ulimg/"+str(lookup(matched_uploads, int(toks[-1])))
                text=text[:l+1]+new_img_src+text[m:]
                print "img tag in action ID {} \"{}\"->\"{}\"".format(itemid, img_src, new_img_src)
            else:
                break

        i = -1
        while True:
            i = text.find('<a', i + 1)
            if i != -1:
                j = text.find('>', i)  # end of a tag
                k = text.find('href=', i)
                assert k < j  # make sure the href attr. belongs to the a tag
                l = k + 5
                invcomma = text[l]
                m = text.find(invcomma, l + 1)
                assert m < j  # make sure the string ends before the end of the a tag

                a_href = text[l+1:m]
                if not "/sample/" in a_href: # this will also be true for ERRONEOUS references of the type "https://localhost/sample..."
                                            # however, the risk exists that we have some external links containing /sample/ that will be rendered useless
                    print "unchanged anchor tag: \"{}\"".format(a_href)
                    continue
                toks = a_href.split('/') # toks[-1] will be the reference to the upload
                new_a_href = "/sample/"+str(lookup(matched_samples, int(toks[-1])))
                text=text[:l+1]+new_a_href+text[m:]
                print "anchor tag in action ID {} \"{}\"->\"{}\"".format(itemid, a_href, new_a_href)
            else:
                break

        return text

    print "\n"+color.RED+color.BOLD+"DATABASE IMPORT\n----------------"+color.END

    src_version = engine.execute("select * from alembic_version").first()[0]
    dst_version = db.engine.execute("select * from alembic_version").first()[0]

    if src_version != dst_version:
        print "You are trying to import a database with an incompatible version"
        return
    if dst_version != "3d9e4225ecbd":
        print "You are trying to import a database that is not compatible with this import script"
        return

    print   "This script will import users, sample and action types, uploads, samples and actions from the source " \
            "database into the main database.\n\n" \
            "It will NOT import shares, i.e. shares have to be set up manually again.\n\n" \
            "Please press ENTER to confirm and CTRL+C to abort."
    raw_input()

    matched_users = match(User, "email", "user")
    matched_sample_types = match(SampleType, "name", "sample type")
    matched_action_types = match(ActionType, "name", "action type")
    matched_uploads = match(Upload, "hash", "upload")
    matched_samples = match(Sample, "name", "sample")

    print   color.BOLD+"\n-----------------------------------------\n"+color.END+"" \
            "Found", len(matched_users), "matched users,", len(matched_sample_types), "matched sample types,", \
            len(matched_action_types), "matched action types,", len(matched_uploads), "matched uploads and", \
            len(matched_samples), "matched samples.\n" \
            "Normally, no matched uploads and no matched samples should have been found. Matched items will not be " \
            "imported as new\n" \
            ""+color.BOLD+"------------------------------------------"+color.END

    print   "\nUnmatched users, sample types and action types will NOW be imported as new.\n" \
            "Please press ENTER to confirm and CTRL+C to abort."
    raw_input()

    # import new users and complete mapping table
    simple_import(User, matched_users, "user")
    for match in matched_users:
        user = dst_sess.query(User).filter(User.id == match[1]).first()
        user.heir_id = None if user.heir_id is None else lookup(matched_users, user.heir_id)
        dst_sess.commit()
    simple_import(SampleType, matched_sample_types, "sample type")
    simple_import(ActionType, matched_action_types, "action type")

    print   "\nUnmatched uploads will NOW be imported.\n" \
            "Please press ENTER to confirm and CTRL+C to abort."
    raw_input()

    # import uploads
    for upload in src_sess.query(Upload).all():
        if upload.hash is None:
            continue
        if upload.id not in [x[0] for x in matched_uploads]:
            print "Importing unmatched upload: ", upload.hash
            old_id = upload.id
            src_sess.expunge(upload)
            make_transient(upload)
            upload.id = None
            upload.user_id = lookup(matched_users, upload.user_id)
            dst_sess.add(upload)
            dst_sess.commit()
            matched_uploads.append((old_id, upload.id))

            if os.path.exists(os.path.join("import/uploads", str(old_id)+"."+upload.ext)):
                if os.path.exists(os.path.join("uploads", str(upload.id)+"."+upload.ext)):
                    print "Cannot import upload file, because it already exists:", os.path.join("uploads", str(upload.id)+"."+upload.ext)
                else:
                    copyfile(os.path.join("import/uploads", str(old_id)+"."+upload.ext), os.path.join("uploads", str(upload.id)+"."+upload.ext))
            else:
                print "Cannot import upload file, because", os.path.join("import/uploads", str(old_id)+"."+upload.ext), "does not exist"

    print   "\nUnmatched samples will NOW be imported.\n" \
            "Please press ENTER to confirm and CTRL+C to abort."
    raw_input()

    # import samples
    # first use simple_import for samples, then correct references using matching table (because samples have cross-
    # references that can only be resolved once everything is imported
    already_matched_samples = matched_samples[:]
    simple_import(Sample, matched_samples, "sample")
    newly_imported = [match for match in matched_samples if match not in already_matched_samples]
    for match in newly_imported:
        sample = dst_sess.query(Sample).filter(Sample.id==match[1]).first()
        sample.owner_id = lookup(matched_users, sample.owner_id)
        sample.sampletype_id = lookup(matched_sample_types, sample.sampletype_id)
        if sample.parent_id > 0:
            sample.parent_id = lookup(matched_samples, sample.parent_id)

        # upload sample image
        if sample.image is not None:
            toks = sample.image.split('/')  # toks[-1] will be the reference to the upload
            sample.image = "/browser/ulimg/" + str(lookup(matched_uploads, int(toks[-1])))

        # update sample description (links and images)
        sample.description = update_html(sample.description, sample.id, matched_uploads, matched_samples)

        dst_sess.commit()

    print   "\nActions will be now imported for NEWLY imported samples. " \
            "While actions are imported, you will be kept informed about references that are being manipulated " \
            "in the action descriptions. Please check if anything seems incorrect.\n" \
            "Please press ENTER to confirm and CTRL+C to abort."
    raw_input()

    # import actions (take into account previous mapping tables)
    imported_action_count = 0
    total_action_count = 0
    for action in src_sess.query(Action).all():
        if action.sample_id in [x[0] for x in newly_imported]:      # check if action belongs to newly imported sample
            old_id = action.id
            src_sess.expunge(action)
            make_transient(action)
            action.id = None
            action.owner_id = lookup(matched_users, action.owner_id)
            action.sample_id = lookup(matched_samples, action.sample_id)
            action.actiontype_id = lookup(matched_action_types, action.actiontype_id)
            action.description = update_html(action.description, old_id, matched_uploads, matched_samples)
            dst_sess.add(action)
            dst_sess.commit()
            imported_action_count += 1
        total_action_count += 1
    print "\nImported", imported_action_count, "out of", total_action_count, "actions"

    # update shared sample table
    # TODO

    print "\n"+color.BOLD+color.RED+"IMPORT IS DONE"+color.END


if __name__ == '__main__':
    manager.run()