from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from app.config.database import connect_to_mongodb, close_mongodb_connection
from app.config.settings import settings
from app.sockets.chat_socket import sio
from app.routes import auth_routes, user_routes, category_routes, listing_routes, offer_routes
from app.routes import wishlist_routes, review_routes, order_routes, payment_routes
from app.routes import chat_routes, admin_routes, notification_routes, upload_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    yield
    await close_mongodb_connection()

api = FastAPI(title=settings.app_name, version="1.0.0",
              description="Bargain Baazaar marketplace API", lifespan=lifespan)
api.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_url],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for router in [auth_routes.router, user_routes.router, category_routes.router, listing_routes.router,
               offer_routes.router, wishlist_routes.router, review_routes.router, order_routes.router,
               payment_routes.router, chat_routes.router, admin_routes.router,
               notification_routes.router, upload_routes.router]:
    api.include_router(router, prefix=settings.api_prefix)

@api.get("/")
async def root():
    return {"message": "Bargain Baazaar API is running", "docs": "/docs"}

@api.get("/health")
async def health():
    return {"success": True, "status": "healthy", "application": "Bargain Baazaar", "currency": "INR", "symbol": "₹"}

app = socketio.ASGIApp(sio, other_asgi_app=api)

