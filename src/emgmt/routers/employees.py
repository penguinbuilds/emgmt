from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.emgmt.models import Employee
from src.emgmt.schemas import (
    EmployeePublic,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeePublicWithDepartmentAndTasks,
)

from src.emgmt.dependencies import get_session
from src.emgmt.utils import hash_password

router = APIRouter()


@router.post("/employees/", tags=["employees"], response_model=EmployeePublic)
async def add_employee(
    *, session: Session = Depends(get_session), employee: EmployeeCreate
):
    employee_data = employee.model_dump(exclude_unset=True)
    password = employee_data.pop("password")
    db_employee = Employee(
        hashed_password=hash_password(password), **employee_data
    )
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee


@router.get(
    "/employees/", tags=["employees"], response_model=list[EmployeePublic]
)
async def display_employees(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    employees = (
        session.execute(select(Employee).offset(offset).limit(limit))
        .scalars()
        .all()
    )
    return employees


@router.get(
    "/employees/{employee_id}",
    tags=["employees"],
    response_model=EmployeePublicWithDepartmentAndTasks,
)
async def get_employee(
    *, session: Session = Depends(get_session), employee_id: UUID
):
    employee = session.get(Employee, str(employee_id))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return employee


@router.patch(
    "/employees/{employee_id}",
    tags=["employees"],
    response_model=EmployeePublic,
)
async def update_employee(
    *,
    session: Session = Depends(get_session),
    employee_id: UUID,
    updated_details: EmployeeUpdate,
):
    db_employee = session.get(Employee, str(employee_id))
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    employee_data = updated_details.model_dump(exclude_unset=True)
    if "password" in employee_data:
        db_employee.hashed_password = hash_password(
            employee_data.pop("password")
        )
        for key, value in employee_data.items():
            setattr(db_employee, key, value)
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee


@router.delete(
    "/employees/{employee_id}",
    tags=["employees"],
)
async def delete_employee(
    *, session: Session = Depends(get_session), employee_id: UUID
):
    employee = session.get(Employee, str(employee_id))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    session.delete(employee)
    session.commit()
    return {"message": "deleted"}
