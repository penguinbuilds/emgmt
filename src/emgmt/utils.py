import json
from typing_extensions import TypeVar

from fastapi import HTTPException
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Result, select
from sqlalchemy.orm import Session

from src.emgmt.models import Base

T = TypeVar("T")


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def save_result_to_json(result: Result, filename: str) -> None:
    columns = result.keys
    data = [dict(zip(columns, row)) for row in result.fetchall()]
    json_data = json.dumps(data, indent=4)

    with open(f"../data/{filename}.json", "w") as file:
        file.write(json_data)


def check_unique_field(
    session: Session,
    model: Base,
    field_name: str,
    value: T,
    error_message: str = "One or more fields have entries that already exist.",
) -> None:
    statement = select(model).where(getattr(model, field_name) == value)
    result = session.execute(statement).first()
    if result:
        raise HTTPException(status_code=409, detail=error_message)
