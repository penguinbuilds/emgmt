from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.emgmt.models import Department
from src.emgmt.schemas import (
    DepartmentPublic,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentPublicWithEmployees,
)

from src.emgmt.dependencies import get_session

router = APIRouter()


@router.post(
    "/departments/", tags=["departments"], response_model=DepartmentPublic
)
async def add_department(
    *, session: Session = Depends(get_session), department: DepartmentCreate
):
    department_data = department.model_dump()
    db_department = Department(**department_data)
    session.add(db_department)
    session.commit()
    session.refresh(db_department)
    return db_department


@router.get(
    "/departments/", tags=["departments"], response_model=list[DepartmentPublic]
)
async def display_departments(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    departments = (
        session.execute(select(Department).offset(offset).limit(limit))
        .scalars()
        .all()
    )
    return departments


@router.get(
    "/departments/{department_id}",
    tags=["departments"],
    response_model=DepartmentPublicWithEmployees,
)
async def get_department(
    *, session: Session = Depends(get_session), department_id: int
):
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found.")
    return department


@router.patch(
    "/departments/{department_id}",
    tags=["departments"],
    response_model=DepartmentPublic,
)
async def update_department(
    *,
    session: Session = Depends(get_session),
    department_id: int,
    updated_details: DepartmentUpdate,
):
    db_department = session.get(Department, department_id)
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found.")
    department_data = updated_details.model_dump(exclude_unset=True)
    for key, value in department_data.items():
        setattr(db_department, key, value)
    session.add(db_department)
    session.commit()
    session.refresh(db_department)
    return db_department


@router.delete(
    "/departments/{department_id}",
    tags=["departments"],
)
async def delete_department(
    *, session: Session = Depends(get_session), department_id: int
):
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    session.delete(department)
    session.commit()
    return {"message": "deleted"}
