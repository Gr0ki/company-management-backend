"""Contains main app initialization."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.settings import get_settings
from .api.routers import api_router


settings = get_settings()
app = FastAPI(debug=settings.DEV)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET, POST, PUT, DELETE, OPTIONS"],
    allow_headers=settings.CORS_HEADERS,
)
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        app=settings.APP_NAME,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEV,
        log_config="logging.conf",
    )
