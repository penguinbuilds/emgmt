from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

# --- Department Schemas ---


class DepartmentBase(BaseModel):
    name: str = Field(unique=True)
    location: str
    date_formed: date | None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentPublic(DepartmentBase):
    id: int


class DepartmentUpdate(BaseModel):
    name: str | None
    location: str | None
    date_formed: date | None


class DepartmentPublicWithEmployees(DepartmentPublic):
    employees: list["EmployeePublic"] = Field(default_factory=list)


# --- Employee Schemas ---


class EmployeeBase(BaseModel):
    name: str
    age: int | None = Field(default=None, ge=18, le=60)
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)
    salary: Decimal | None

    department_id: int | None = Field(default=None)


class EmployeeCreate(EmployeeBase):
    password: str


class EmployeePublic(EmployeeBase):
    id: UUID


class EmployeeUpdate(BaseModel):
    name: str | None
    age: int | None = Field(default=None, ge=18, le=60)
    username: str | None
    email: EmailStr | None
    password: str | None = Field(default=None)
    salary: Decimal | None
    department_id: int | None


class EmployeePublicWithDepartmentAndTasks(EmployeePublic):
    department: DepartmentPublic | None = None
    tasks: list["TaskPublic"] = Field(default_factory=list)


# --- Task Schemas ---


class TaskBase(BaseModel):
    title: str
    description: str | None
    completed: bool

    employee_id: UUID


class TaskPublic(TaskBase):
    id: int


# --- Forward references ---
DepartmentPublicWithEmployees.model_rebuild()
EmployeePublicWithDepartmentAndTasks.model_rebuild()
