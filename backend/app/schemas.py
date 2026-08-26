from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models import ApplicationStatus, EmploymentType, Role


# ---------- Auth / Users ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    role: Role = Role.candidate


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ---------- Jobs ----------

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    location: str
    skills: str = ""
    employment_type: EmploymentType = EmploymentType.full_time
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_active: Optional[bool] = None


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    description: str
    location: str
    skills: str
    employment_type: EmploymentType
    salary_min: Optional[float]
    salary_max: Optional[float]
    is_active: bool
    created_at: datetime
    posted_by_id: int

    class Config:
        from_attributes = True


class JobListOut(BaseModel):
    total: int
    items: list[JobOut]


# ---------- Applications ----------

class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    cover_letter: Optional[str]
    status: ApplicationStatus
    created_at: datetime

    class Config:
        from_attributes = True
