from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time

from app.config import settings
from app.api import auth, exploitations, data_collection, analytics, parcelles

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

@app.middleware("http")
async def tracking_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", f"req-{int(time.time() * 1000)}")

    response = await call_next(request)
    process_time = time.time() - start_time

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    logger.info(f"{request_id} {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to AgriData Platform",
        "version": settings.APP_VERSION,
        "docs": f"{settings.DOCS_URL}",
    }

app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(exploitations.router, prefix=f"{settings.API_PREFIX}/exploitations", tags=["Exploitations"])
app.include_router(parcelles.router, prefix=f"{settings.API_PREFIX}/parcelles", tags=["Parcelles"])
app.include_router(data_collection.router, prefix=f"{settings.API_PREFIX}/data", tags=["Data Collection"])
app.include_router(analytics.router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up AgriData Platform...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AgriData Platform...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
