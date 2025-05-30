from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Any

from models.applications.applications_model import ApplicationStatus


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ResponseOut(BaseModel):
    id: int
    question_id: int
    answer_text: Optional[str] = None
    question_text: Optional[str] = None
    question_order: Optional[int] = None

    class Config:
        orm_mode = True


class ApplicationOut(BaseModel):
    id: int
    form_id: int
    user_id: str
    submitted_at: datetime
    status: ApplicationStatus

    class Config:
        orm_mode = True


class ApplicationDetailOut(BaseModel):
    id: int
    form_id: int
    user_id: str
    user_email: str
    is_club_member: bool
    form_name: Optional[str] = None
    club_id: Optional[str] = None
    submitted_at: datetime
    status: ApplicationStatus
    responses: List[ResponseOut] = []
    endorser_ids: List[str] = []
    endorser_count: int = 0

    class Config:
        orm_mode = True

class UserApplicationOut(BaseModel):
    id: int
    form_id: int
    form_name: Optional[str] = None
    club_id: Optional[str] = None
    club_name: Optional[str] = None
    status: ApplicationStatus
    endorser_ids: List[str] = []
    endorser_count: int = 0
    submitted_at: datetime

    class Config:
        orm_mode = True

class FormApplicationOut(BaseModel):
    id: int
    user_id: str
    user_name: str
    user_email: str
    form_id: int
    status: ApplicationStatus
    endorser_ids: List[str] = []
    endorser_count: int = 0
    submitted_at: datetime

    class Config:
        orm_mode = True