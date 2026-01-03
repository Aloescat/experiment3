# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
import uuid
from typing import List, Optional


# ============ 学生CRUD操作 ============
def get_student(db: Session, student_id: uuid.UUID):
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def get_student_by_email(db: Session, email: str):
    return db.query(models.Student).filter(models.Student.email == email).first()


def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).offset(skip).limit(limit).all()


def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, student_id: uuid.UUID, student_update: schemas.StudentUpdate):
    db_student = get_student(db, student_id)
    if not db_student:
        return None
    
    update_data = student_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: uuid.UUID):
    db_student = get_student(db, student_id)
    if db_student:
        db.delete(db_student)
        db.commit()
        return True
    return False


# ============ 组CRUD操作 ============
def get_group(db: Session, group_id: uuid.UUID):
    return db.query(models.Group).filter(models.Group.id == group_id).first()


def get_group_by_name(db: Session, name: str):
    return db.query(models.Group).filter(models.Group.name == name).first()


def get_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Group).offset(skip).limit(limit).all()


def create_group(db: Session, group: schemas.GroupCreate):
    db_group = models.Group(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def update_group(db: Session, group_id: uuid.UUID, group_update: schemas.GroupUpdate):
    db_group = get_group(db, group_id)
    if not db_group:
        return None
    
    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_group, field, value)
    
    db.commit()
    db.refresh(db_group)
    return db_group


def delete_group(db: Session, group_id: uuid.UUID):
    db_group = get_group(db, group_id)
    if db_group:
        db.delete(db_group)
        db.commit()
        return True
    return False


# ============ 学生-组关系操作 ============
def add_student_to_group(db: Session, student_id: uuid.UUID, group_id: uuid.UUID):
    student = get_student(db, student_id)
    group = get_group(db, group_id)
    
    if not student or not group:
        return None
    
    student.group_id = group_id
    db.commit()
    db.refresh(student)
    return student


def remove_student_from_group(db: Session, student_id: uuid.UUID, group_id: uuid.UUID):
    student = get_student(db, student_id)
    
    if not student or student.group_id != group_id:
        return None
    
    student.group_id = None
    db.commit()
    db.refresh(student)
    return student


def get_students_in_group(db: Session, group_id: uuid.UUID):
    group = get_group(db, group_id)
    if not group:
        return None
    
    return group.students


def transfer_student(db: Session, student_id: uuid.UUID, from_group_id: uuid.UUID, to_group_id: uuid.UUID):
    student = get_student(db, student_id)
    from_group = get_group(db, from_group_id)
    to_group = get_group(db, to_group_id)
    
    if not student or not from_group or not to_group:
        return None
    
    if student.group_id != from_group_id:
        return None
    
    student.group_id = to_group_id
    db.commit()
    db.refresh(student)
    return student


def get_group_with_students(db: Session, group_id: uuid.UUID):
    group = get_group(db, group_id)
    if group:
        # 添加学生数量
        student_count = len(group.students)
        return group, student_count
    return None, 0