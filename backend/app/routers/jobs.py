from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import EmploymentType, Job, Role, User
from app.schemas import JobCreate, JobListOut, JobOut, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListOut)
def list_jobs(
    q: Optional[str] = Query(None, description="Free text search across title/company/description"),
    location: Optional[str] = None,
    skill: Optional[str] = None,
    employment_type: Optional[EmploymentType] = None,
    min_salary: Optional[float] = None,
    max_salary: Optional[float] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Job).filter(Job.is_active.is_(True))

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(Job.title.ilike(like), Job.company.ilike(like), Job.description.ilike(like))
        )
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if skill:
        query = query.filter(Job.skills.ilike(f"%{skill}%"))
    if employment_type:
        query = query.filter(Job.employment_type == employment_type)
    if min_salary is not None:
        query = query.filter(Job.salary_max >= min_salary)
    if max_salary is not None:
        query = query.filter(Job.salary_min <= max_salary)

    total = query.count()
    items = (
        query.order_by(Job.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return JobListOut(total=total, items=items)


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.recruiter, Role.admin)),
):
    job = Job(**job_in.model_dump(), posted_by_id=current_user.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.put("/{job_id}", response_model=JobOut)
def update_job(
    job_id: int,
    job_in: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.recruiter, Role.admin)),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if current_user.role != Role.admin and job.posted_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own job postings")

    for field, value in job_in.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.recruiter, Role.admin)),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if current_user.role != Role.admin and job.posted_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own job postings")
    db.delete(job)
    db.commit()
    return None
