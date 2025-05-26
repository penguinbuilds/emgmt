from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from src.emgmt.schemas import (
    Department,
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
    db_department = Department.model_validate(department)
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
    departments = session.exec(
        select(Department).offset(offset).limit(limit)
    ).all()
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
    db_department.sqlmodel_update(department_data)
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
