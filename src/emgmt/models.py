from datetime import date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    # UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    date_formed: Mapped[date] = mapped_column(Date, nullable=True)

    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        # cascade="all, delete-orphan"
    )


class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)
    salary: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("department.id"), nullable=True
    )

    department: Mapped[Department | None] = relationship(
        "Department", back_populates="employees"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="employee"
    )

    # __table_args__ = (
    #     UniqueConstraint("username", name="uq_employee_username"),
    #     UniqueConstraint("email", name="uq_employee_email"),
    # )


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False
    )

    employee: Mapped[Employee] = relationship(
        "Employee", back_populates="tasks"
    )
