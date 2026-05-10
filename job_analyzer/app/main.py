from fastapi import FastAPI
from app.routers import jobs

app = FastAPI(title="Job Analyzer AI")

app.include_router(jobs.router)
