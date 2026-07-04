from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.handlers import router

app = FastAPI(title="LLM SQL Search API")
app.mount("/output", StaticFiles(directory="output"), name="output")
app.include_router(router, prefix="/api")