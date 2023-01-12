import time

from fastapi import FastAPI, Request

from src.middlewares.process_time import ProcessTimeMiddleware
from src.routes import notes, users, auth

app = FastAPI()

# executes for each request
app.add_middleware(ProcessTimeMiddleware)

app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "TODO App v1.01"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
