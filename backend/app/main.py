from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

from app.config import settings
from app.database import create_tables
from app.schemas import ApiResponse
from app.routers import auth_router, search_history_router
from app.routers.upload_router import router as upload_router
from app.routers.search import router as search_router

app_ready = False



@asynccontextmanager
async def lifespan(app: FastAPI):
    async def init_db():
        global app_ready
        try:
            await create_tables()
            app_ready = True
        except Exception as e:
            print("DB init failed:", e)

    asyncio.create_task(init_db())
    yield



app = FastAPI(
    title=settings.app_name,
    description="PDF Vector Search Engine API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            success=False,
            data=None,
            message=exc.detail,
        ).model_dump(),
    )


# ROUTERS
app.include_router(auth_router, prefix="/api/auth")
app.include_router(search_history_router, prefix="/api")
app.include_router(upload_router, prefix="/api")

app.include_router(search_router, prefix="/api")


@app.get("/health")
async def health_check():
    if not app_ready:
        return JSONResponse(
            status_code=503,
            content={"status": "starting"}
        )

    return {"status": "healthy", "app": settings.app_name}



@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
    }
