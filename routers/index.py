from . import accounts, listings, conversations, images


def load_routes(app):
    app.include_router(accounts.router)
    app.include_router(listings.router)
    app.include_router(conversations.router)
    app.include_router(images.router)