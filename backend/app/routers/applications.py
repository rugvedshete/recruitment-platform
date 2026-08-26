from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import Application, Job, Role, User
from app.schemas import ApplicationCreate, ApplicationOut, ApplicationStatusUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    app_in: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.candidate)),
):
    job = db.query(Job).filter(Job.id == app_in.job_id, Job.is_active.is_(True)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or inactive")

    existing = (
        db.query(Application)
        .filter(Application.job_id == app_in.job_id, Application.candidate_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this job")

    application = Application(
        job_id=app_in.job_id,
        candidate_id=current_user.id,
        cover_letter=app_in.cover_letter,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/me", response_model=list[ApplicationOut])
def my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.candidate)),
):
    return (
        db.query(Application)
        .filter(Application.candidate_id == current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )


@router.get("/job/{job_id}", response_model=list[ApplicationOut])
def applications_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.recruiter, Role.admin)),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if current_user.role != Role.admin and job.posted_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view applicants for your own jobs")

    return db.query(Application).filter(Application.job_id == job_id).all()


@router.put("/{application_id}/status", response_model=ApplicationOut)
def update_application_status(
    application_id: int,
    status_in: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.recruiter, Role.admin)),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if current_user.role != Role.admin and job.posted_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only manage applicants for your own jobs")

    application.status = status_in.status
    db.commit()
    db.refresh(application)
    return application
