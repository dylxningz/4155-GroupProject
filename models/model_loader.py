from . import accounts
from dependencies.database import engine


def index():
    accounts.Base.metadata.create_all(engine)
