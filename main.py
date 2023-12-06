from fastapi import FastAPI

from auth.routers import router as auth_router
from job.routers import router as job_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(job_router, prefix="/job", tags=["Job"])
