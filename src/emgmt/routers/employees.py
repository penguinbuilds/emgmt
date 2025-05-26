from uuid import uuid4, UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from src.emgmt.schemas import (
    Employee,
    EmployeePublic,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeePublicWithDepartment,
)

# from src.emgmt.database import engine
from src.emgmt.utils import hash_password
from src.emgmt.dependencies import get_session

router = APIRouter()


@router.post("/employees/", tags=["employees"], response_model=EmployeePublic)
async def add_employee(
    *, session: Session = Depends(get_session), employee: EmployeeCreate
):
    # with Session(engine) as session:
    db_employee = Employee.model_validate(employee)
    db_employee.id = uuid4()
    db_employee.hashed_password = hash_password(employee.password)
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
    # with Session(engine) as session:
    employees = session.exec(select(Employee).offset(offset).limit(limit)).all()
    return employees


@router.get(
    "/employees/{employee_id}",
    tags=["employees"],
    response_model=EmployeePublicWithDepartment,
)
async def get_employee(
    *, session: Session = Depends(get_session), employee_id: UUID
):
    # with Session(engine) as session:
    employee = session.get(Employee, employee_id)
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
    # with Session(engine) as session:
    db_employee = session.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    employee_data = updated_details.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in employee_data:
        password = employee_data["password"]
        hashed_password = hash_password(password)
        extra_data["hashed_password"] = hashed_password
    db_employee.sqlmodel_update(employee_data, update=extra_data)
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
    # with Session(engine) as session:
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    session.delete(employee)
    session.commit()
    return {"message": "deleted"}
