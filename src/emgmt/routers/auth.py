from typing_extensions import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.emgmt.database import get_db
from src.emgmt.models import Employee
from src.emgmt.utils import verify_password, create_access_token, decode_token


router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/")


async def get_authenticated_employee(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_db),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        employee_data = payload.get("data")

        if not employee_data or "id" not in employee_data:
            raise credentials_exception

        employee_id = UUID(employee_data["id"])

        result = session.execute(
            select(Employee.id, Employee.role, Employee.username).where(
                Employee.id == employee_id
            )
        ).first()

        if result:
            employee_info = result._asdict()
        else:
            employee_info = None

        if not employee_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Employee not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return employee_info

    except InvalidTokenError:
        raise credentials_exception
    except HTTPException:
        raise
    except Exception as e:
        raise e


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        auth_employee_info: dict = Depends(get_authenticated_employee),
    ):
        if auth_employee_info["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return auth_employee_info["id"]


require_admin = RoleChecker(["admin"])


@router.post("/")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_db),
):
    employee = session.execute(
        select(Employee).where(Employee.username == form_data.username)
    ).scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=400, detail="User does not exists.")
    if not verify_password(form_data.password, employee.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    token_data = {
        "username": employee.username,
        "email": employee.email,
        "id": str(employee.id),
    }

    return {
        "access_token": create_access_token(token_data),
        "token_type": "bearer",
    }
