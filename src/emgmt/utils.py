from datetime import datetime, timedelta
import json
from typing_extensions import TypeVar
from uuid import uuid4

from fastapi import HTTPException, status
from httpx import AsyncClient
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Result, select
from sqlalchemy.orm import Session

from src.emgmt.config import settings
from src.emgmt.database import get_db
from src.emgmt.models import Base, Employee

T = TypeVar("T")


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(password, hashed_password)


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


def create_access_token(
    data: dict,
    expiry: timedelta = None,
    refresh: bool = False,
) -> str:
    payload = {}

    expiry_datetime = datetime.now() + (
        expiry
        if expiry is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload["data"] = data
    payload["expiry"] = expiry_datetime.isoformat()
    payload["jwt_id"] = str(uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return token


def create_refresh_token(
    data: dict,
    expiry: timedelta = None,
    refresh: bool = False,
) -> str:
    payload = {}

    expiry_datetime = datetime.now() + (
        expiry
        if expiry is not None
        else timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )

    payload["data"] = data
    payload["expiry"] = expiry_datetime.isoformat()
    payload["jwt_id"] = str(uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload,
        key=settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return token_data
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def create_admin_user():
    db = next(get_db())
    try:
        admin_exists = db.execute(
            select(Employee).where(Employee.username == "admin")
        ).scalar_one_or_none()

        if not admin_exists:
            admin_user = Employee(
                username="admin",
                email="admin@company.com",
                name="Admin",
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
                department_id=None,
                tasks=[],
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully.")
    finally:
        db.close()


async def get_client():
    async with AsyncClient() as client:
        yield client
