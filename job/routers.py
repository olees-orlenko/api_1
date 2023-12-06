from fastapi import APIRouter, Depends, HTTPException

from auth.database import User, get_job, update_user_credit
from auth.routers import auth_handler

router = APIRouter()


def get_current_user(token: str = Depends(auth_handler.get_token)):
    if token is not None:
        return token
    else:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


@router.post("/start_job/")
def start_job(job_id: int, current_user: User = Depends(get_current_user)):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if current_user.credit < job.price:
        raise HTTPException(status_code=400, detail="Not enough credit to start a job")
    current_user.credit -= job.price
    update_user_credit(current_user)
    return {"message": "Job started successfully"}
