from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.api import answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
)

app.include_router(answer.router, prefix="/answer")
