# app/schemas.py
from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional, List
import uuid


# ============ 基础模型 ============
class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    group_id: Optional[uuid.UUID] = None


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


# ============ 创建请求模型 ============
class StudentCreate(StudentBase):
    pass


class GroupCreate(GroupBase):
    pass


# ============ 更新请求模型 ============
class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    group_id: Optional[uuid.UUID] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# ============ 响应模型 ============
class StudentResponse(StudentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GroupResponse(GroupBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    student_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class GroupWithStudents(GroupResponse):
    students: List[StudentResponse] = []


class StudentWithGroup(StudentResponse):
    group: Optional[GroupResponse] = None


# ============ 操作请求模型 ============
class AddStudentToGroup(BaseModel):
    student_id: uuid.UUID
    group_id: uuid.UUID


class TransferStudent(BaseModel):
    student_id: uuid.UUID
    from_group_id: uuid.UUID
    to_group_id: uuid.UUID


class RemoveStudentFromGroup(BaseModel):
    student_id: uuid.UUID
    group_id: uuid.UUID