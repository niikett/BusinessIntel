from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import *
from app.schemas import *
from app.core.config import settings
from app.api.routes import *


# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI()


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/dummy-route")
async def dummy_route():
    return "Dummy route."


app.include_router(attendances.router)
app.include_router(auth.router)
app.include_router(comments.router)
app.include_router(courses.router)
app.include_router(institutes.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(profiles.router)
app.include_router(results.router)
