from .news import News, LinkUserNews
from .sample import Sample
from .share import Share
from .user import current_user


def deleted_sample_handler(session, sample):
    def recursive(sample):
        # move everything that is mounted here back to the root
        session.execute(
            Share.__table__.update().values(mountpoint_id=0).where(Share.mountpoint_id == sample.id)
        )

        # go down the hierarchy and perform the same operations
        for s in sample.children:
            recursive(s)

            if s.owner == current_user():
                # if the sample down the hierarchy belongs to the current user,
                # also mark it as deleted
                session.execute(
                    Sample.__table__.update().values(isdeleted=True).where(Sample.id == s.id)
                )
                # delete all corresponding news
                for news in session.execute(News.__table__.select().where(News.sample_id == s.id)):
                    news_id = news[0]
                    session.execute(
                        LinkUserNews.__table__.delete().where(LinkUserNews.news_id == news_id)
                    )
                session.execute(News.__table__.delete().where(News.sample_id == s.id))
                # and delete all corresponding shares
                session.execute(Share.__table__.delete().where(Share.sample_id == s.id))
                # NB: if another user has children underneath this sample, they have been taken
                #     care of previously; idem if another user has mounted samples underneath
                #     this sample
            else:
                # otherwise it belongs to someone else and we move it back to that person's root
                session.execute(
                    Sample.__table__.update().values(parent_id=0).where(Sample.id == s.id)
                )
                # If there is some news associated with the sample or a subsample, this is not
                # really an issue. Everybody who has access to the sample - and the person who
                # created the news, will still see the news - but the person who created the
                # news will not be able to access the sample (and therefore not be able to
                # deactivate the news). Two possible solutions:
                # - wait for the news to expire
                # - give the user access again so he/she can deactivate the news
                # TODO: careful with duplicate sample names here

    # delete all corresponding shares
    session.execute(Share.__table__.delete().where(Share.sample_id == sample.id))

    # delete all corresponding news
    for news in session.execute(News.__table__.select().where(News.sample_id == sample.id)):
        news_id = news[0]
        session.execute(LinkUserNews.__table__.delete().where(LinkUserNews.news_id == news_id))
    session.execute(News.__table__.delete().where(News.sample_id == sample.id))

    recursive(sample)


def deleted_share_handler(session, share):
    def recursive(sample):
        # move samples mounted here back to the root for the user whose share we remove
        session.execute(
            Share.__table__.update()
            .values(mountpoint_id=0)
            .where(Share.user == share.user and Share.mountpoint == sample)
        )

        # go down the hierarchy and perform the same operations
        for s in sample.children:
            recursive(s)

            # check if child or mounted sample belongs to the user whose share we remove
            # and move it back to his tree
            if s.owner == share.user:
                session.execute(
                    Sample.__table__.update().values(parent_id=0).where(Sample.id == s.id)
                )
                # If there is some news associated with the sample or a subsample, this is not
                # really an issue. Everybody who has access to the sample - and the person who
                # created the news, will still see the news - but the person who created the
                # news will not be able to access the sample (and therefore not be able to
                # deactivate the news). Two possible solutions:
                # - wait for the news to expire
                # - give the user access again so he/she can deactivate the news
                # TODO: careful with duplicate sample names here

    recursive(share.sample)


# https://stackoverflow.com/questions/13693872/can-sqlalchemy-events-be-used-to-update-a-denormalized-data-cache/13765857#13765857
# https://github.com/pallets/flask-sqlalchemy/issues/182
def after_flush(session, flush_context):
    """- check for any deleted samples or shares
    NB: This had to be done after the flush, because if a parent sample / mountpoint was deleted,
    the database would automatically set the corresponding foreign keys to NULL. Not sure if this
    still applies since we are not really deleting samples anymore.
    """
    for obj in session.dirty:
        if isinstance(obj, Sample) and obj.isdeleted:  # detected sample deletion
            deleted_sample_handler(session, obj)

    for obj in session.deleted:
        if isinstance(obj, Share):  # detected share deletion
            deleted_share_handler(session, obj)
