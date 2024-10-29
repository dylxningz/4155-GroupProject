from . import accounts, listings, conversations, images
from dependencies.database import engine


def index():
    accounts.Base.metadata.create_all(engine)
    listings.Base.metadata.create_all(engine)
    conversations.Base.metadata.create_all(engine)
    images.Base.metadata.create_all(engine)
