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

from src.emgmt.database import get_db
from src.emgmt.routers.auth import require_admin
from src.emgmt.schemas import EmployeePublicWithDepartmentAndTasks

router = APIRouter(prefix="/departments", tags=["departments"])


@router.post("/", response_model=DepartmentPublic)
async def add_department(
    department: DepartmentCreate,
    session: Session = Depends(get_db),
    current_user: EmployeePublicWithDepartmentAndTasks = Depends(require_admin),
):
    department_data = department.model_dump()
    db_department = Department(**department_data)
    session.add(db_department)
    session.commit()
    session.refresh(db_department)
    return db_department


@router.get("/", response_model=list[DepartmentPublic])
async def display_departments(
    session: Session = Depends(get_db),
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
    "/{department_id}",
    response_model=DepartmentPublicWithEmployees,
)
async def get_department(
    department_id: int,
    session: Session = Depends(get_db),
    current_user: EmployeePublicWithDepartmentAndTasks = Depends(require_admin),
    # to do: change authorization so that employees belonging to that department can also view details
):
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found.")
    return department


@router.patch(
    "/{department_id}",
    response_model=DepartmentPublic,
)
async def update_department(
    department_id: int,
    updated_details: DepartmentUpdate,
    session: Session = Depends(get_db),
    current_user: EmployeePublicWithDepartmentAndTasks = Depends(require_admin),
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
    "/{department_id}",
)
async def delete_department(
    department_id: int,
    session: Session = Depends(get_db),
    current_user: EmployeePublicWithDepartmentAndTasks = Depends(require_admin),
):
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    session.delete(department)
    session.commit()
    return {"message": "deleted"}
