from . import accounts, listings
from dependencies.database import engine


def index():
    accounts.Base.metadata.create_all(engine)
    listings.Base.metadata.create_all(engine)
