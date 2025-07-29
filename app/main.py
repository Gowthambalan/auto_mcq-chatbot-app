# main.py
from fastapi import FastAPI
from app.routes import query, upload, ingest

app = FastAPI()

app.include_router(upload.router)
app.include_router(ingest.router)
app.include_router(query.router)
