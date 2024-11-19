from . import accounts, listings, conversations, images,favorite


def load_routes(app):
    app.include_router(accounts.router)
    app.include_router(listings.router)
    app.include_router(conversations.router)
    app.include_router(images.router)
    app.include_router(favorite.router)