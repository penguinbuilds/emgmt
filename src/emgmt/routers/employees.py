from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.emgmt.models import Employee, Department
from src.emgmt.schemas import (
    EmployeePublic,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeePublicWithDepartmentAndTasks,
)

from src.emgmt.database import get_db
from src.emgmt.utils import hash_password, check_unique_field

router = APIRouter(prefix="/employees", tags=["employees"])


def enforce_and_validate_employee_constraints(
    session: Session, db_employee: Employee
):
    department_ids = session.execute(select(Department.id)).scalars().all()
    if (
        db_employee.department_id is not None
        and db_employee.department_id not in department_ids
    ):
        raise HTTPException(
            status_code=409, detail="Invalid department id entered."
        )

    check_unique_field(
        session=session,
        model=Employee,
        field_name="username",
        value=db_employee.username,
        error_message="Username is already in use.",
    )
    check_unique_field(
        session=session,
        model=Employee,
        field_name="email",
        value=db_employee.email,
        error_message="Email is already in use.",
    )


@router.post("/", response_model=EmployeePublic)
async def add_employee(
    employee: EmployeeCreate, session: Session = Depends(get_db)
):
    employee_data = employee.model_dump(exclude_unset=True)
    password = employee_data.pop("password")
    db_employee = Employee(
        hashed_password=hash_password(password), **employee_data
    )
    enforce_and_validate_employee_constraints(session, db_employee)
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee


@router.get("/", response_model=list[EmployeePublic])
async def display_employees(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_db),
):
    employees = (
        session.execute(select(Employee).offset(offset).limit(limit))
        .scalars()
        .all()
    )
    return employees


@router.get(
    "/{employee_id}",
    response_model=EmployeePublicWithDepartmentAndTasks,
)
async def get_employee(employee_id: UUID, session: Session = Depends(get_db)):
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return employee


@router.patch(
    "/{employee_id}",
    response_model=EmployeePublic,
)
async def update_employee(
    employee_id: UUID,
    updated_details: EmployeeUpdate,
    session: Session = Depends(get_db),
):
    db_employee = session.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    employee_data = updated_details.model_dump(exclude_unset=True)
    if "password" in employee_data:
        db_employee.hashed_password = hash_password(
            employee_data.pop("password")
        )
        for key, value in employee_data.items():
            setattr(db_employee, key, value)
    enforce_and_validate_employee_constraints(session, db_employee)
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee


@router.delete(
    "/{employee_id}",
)
async def delete_employee(
    employee_id: UUID, session: Session = Depends(get_db)
):
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    session.delete(employee)
    session.commit()
    return {"message": "deleted"}
