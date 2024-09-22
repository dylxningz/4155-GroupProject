from . import accounts, listings


def load_routes(app):
    app.include_router(accounts.router)
    app.include_router(listings.router)

