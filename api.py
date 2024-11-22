import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event

from dependencies.config import conf
from models import model_loader
from routers import index as index_router
from fastapi.routing import APIWebSocketRoute
from routers import conversations
from fastapi.routing import APIRoute

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_loader.index()
index_router.load_routes(app)
app.include_router(conversations.router)

for route in app.routes:
    if isinstance(route, APIWebSocketRoute):
        print(f"WebSocket Path: {route.path}")
    elif isinstance(route, APIRoute):
        print(f"HTTP Path: {route.path}, Methods: {route.methods}")

if __name__ == "__main__":
    uvicorn.run(app, host=conf.app_host, port=conf.app_port)