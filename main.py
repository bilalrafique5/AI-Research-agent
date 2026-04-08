from fastapi import FastAPI
from api.routes import router

app=FastAPI(title="AI Research Agent")

app.include_router(router)

