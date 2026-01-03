# app/endpoints/students.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # 检查邮箱是否已存在
    db_student = crud.get_student_by_email(db, email=student.email)
    if db_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 如果提供了group_id，验证组是否存在
    if student.group_id:
        db_group = crud.get_group(db, group_id=student.group_id)
        if not db_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
    
    return crud.create_student(db=db, student=student)


@router.get("/", response_model=List[schemas.StudentResponse])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = crud.get_students(db, skip=skip, limit=limit)
    return students


@router.get("/{student_id}", response_model=schemas.StudentWithGroup)
def read_student(student_id: uuid.UUID, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Student not found"
        )
    return db_student


@router.put("/{student_id}", response_model=schemas.StudentResponse)
def update_student(
    student_id: uuid.UUID, 
    student_update: schemas.StudentUpdate, 
    db: Session = Depends(get_db)
):
    db_student = crud.update_student(db, student_id=student_id, student_update=student_update)
    if db_student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Student not found"
        )
    return db_student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: uuid.UUID, db: Session = Depends(get_db)):
    success = crud.delete_student(db, student_id=student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Student not found"
        )
    return None