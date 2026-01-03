# app/endpoints/groups.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=schemas.GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    # 检查组名是否已存在
    db_group = crud.get_group_by_name(db, name=group.name)
    if db_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group name already exists"
        )
    return crud.create_group(db=db, group=group)


@router.get("/", response_model=List[schemas.GroupResponse])
def read_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    groups = crud.get_groups(db, skip=skip, limit=limit)
    # 添加学生数量到响应
    result = []
    for group in groups:
        group_dict = {**group.__dict__}
        group_dict["student_count"] = len(group.students)
        result.append(schemas.GroupResponse(**group_dict))
    return result


@router.get("/{group_id}", response_model=schemas.GroupWithStudents)
def read_group(group_id: uuid.UUID, db: Session = Depends(get_db)):
    group, student_count = crud.get_group_with_students(db, group_id=group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Group not found"
        )
    
    # 创建包含学生信息的响应
    group_dict = {**group.__dict__}
    group_dict["student_count"] = student_count
    group_dict["students"] = group.students
    
    return schemas.GroupWithStudents(**group_dict)


@router.put("/{group_id}", response_model=schemas.GroupResponse)
def update_group(
    group_id: uuid.UUID, 
    group_update: schemas.GroupUpdate, 
    db: Session = Depends(get_db)
):
    # 如果更新名称，检查是否重复
    if group_update.name:
        existing_group = crud.get_group_by_name(db, name=group_update.name)
        if existing_group and existing_group.id != group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group name already exists"
            )
    
    db_group = crud.update_group(db, group_id=group_id, group_update=group_update)
    if db_group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Group not found"
        )
    
    # 添加学生数量到响应
    group_dict = {**db_group.__dict__}
    group_dict["student_count"] = len(db_group.students)
    return schemas.GroupResponse(**group_dict)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: uuid.UUID, db: Session = Depends(get_db)):
    success = crud.delete_group(db, group_id=group_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Group not found"
        )
    return None


@router.post("/add-student", response_model=schemas.StudentResponse)
def add_student_to_group(
    data: schemas.AddStudentToGroup,
    db: Session = Depends(get_db)
):
    result = crud.add_student_to_group(
        db, 
        student_id=data.student_id, 
        group_id=data.group_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student or group not found"
        )
    return result


@router.delete("/remove-student", response_model=schemas.StudentResponse)
def remove_student_from_group(
    data: schemas.RemoveStudentFromGroup,
    db: Session = Depends(get_db)
):
    result = crud.remove_student_from_group(
        db,
        student_id=data.student_id,
        group_id=data.group_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found in this group"
        )
    return result


@router.get("/{group_id}/students", response_model=List[schemas.StudentResponse])
def get_students_in_group(group_id: uuid.UUID, db: Session = Depends(get_db)):
    students = crud.get_students_in_group(db, group_id=group_id)
    if students is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return students


@router.post("/transfer-student", response_model=schemas.StudentResponse)
def transfer_student(
    data: schemas.TransferStudent,
    db: Session = Depends(get_db)
):
    result = crud.transfer_student(
        db,
        student_id=data.student_id,
        from_group_id=data.from_group_id,
        to_group_id=data.to_group_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student or groups not found, or student is not in the specified group"
        )
    return result