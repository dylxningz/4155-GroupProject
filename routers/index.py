from . import accounts


def load_routes(app):
    app.include_router(accounts.router)
