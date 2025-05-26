from uuid import UUID

from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr


# class Department(SQLModel, table=True):
#     id: UUID | None = Field(default=None, primary_key=True)
#     name: str | None = Field(default=None)
#     location: str | None = Field(default=None)


class DepartmentBase(SQLModel):
    name: str | None = Field(default=None)
    location: str | None = Field(default=None)


class Department(DepartmentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    employees: list["Employee"] = Relationship(back_populates="department")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentPublic(DepartmentBase):
    id: int


class DepartmentUpdate(SQLModel):
    name: str | None = Field(default=None)
    location: str | None = Field(default=None)


class EmployeeBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, ge=18, le=60)
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)

    department_id: int | None = Field(default=None, foreign_key="department.id")


class Employee(EmployeeBase, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    hashed_password: str | None = Field(default=None)

    department: Department | None = Relationship(back_populates="employees")


class EmployeeCreate(EmployeeBase):
    password: str


class EmployeePublic(EmployeeBase):
    id: UUID


class EmployeeUpdate(SQLModel):
    name: str | None
    age: int | None = Field(default=None, ge=18, le=60)
    username: str | None
    email: EmailStr | None
    password: str | None = Field(default=None)

    team_id: int | None = None


class EmployeePublicWithDepartment(EmployeePublic):
    department: DepartmentPublic | None = None


class DepartmentPublicWithEmployees(DepartmentPublic):
    employees: list[EmployeePublic] = []
