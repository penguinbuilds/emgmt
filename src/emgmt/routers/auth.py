from datetime import datetime, timedelta
from typing_extensions import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.emgmt.config import settings
from src.emgmt.database import get_db
from src.emgmt.models import Employee
from src.emgmt.schemas import EmployeePublicWithDepartmentAndTasks
from src.emgmt.utils import verify_password


router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/")


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


# async def get_logged_in_employee(
#     token: Annotated[str, Depends(oauth2_scheme)],
#     session: Session = Depends(get_db),
# ) -> EmployeePublicWithDepartmentAndTasks:
#     try:
#         payload = decode_token(token)
#         employee_data = payload.get("data")
#         if not employee_data or "id" not in employee_data:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid authentication credentials",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         employee_id = employee_data["id"]
#         db_employee = session.get(Employee, (employee_id))
#         if not db_employee:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Employee not found",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         return EmployeePublicWithDepartmentAndTasks.model_validate(db_employee)
#     except InvalidTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid Token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )


class AuthenticatedEmployee:
    def __init__(
        self, employee: EmployeePublicWithDepartmentAndTasks, role: str
    ):
        self.employee = employee
        self.role = role

    def __getattr__(self, name):
        # Delegate attribute access to the employee object
        return getattr(self.employee, name)


# class RoleChecker:
#     def __init__(self, allowed_roles: list[str]):
#         self.allowed_roles = allowed_roles

#     def __call__(
#         self,
#         current_user: EmployeePublicWithDepartmentAndTasks = Depends(
#             get_logged_in_employee
#         ),
#     ):
#         if (
#             not hasattr(current_user, "role")
#             or current_user.role not in self.allowed_roles
#         ):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Insufficient permissions",
#             )
#         return current_user


async def get_authenticated_employee(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_db),
) -> AuthenticatedEmployee:
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

        db_employee = session.get(Employee, employee_id)
        if not db_employee:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Employee not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        employee_public = EmployeePublicWithDepartmentAndTasks.model_validate(
            db_employee
        )
        return AuthenticatedEmployee(employee_public, db_employee.role)

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
        auth_employee: AuthenticatedEmployee = Depends(
            get_authenticated_employee
        ),
    ):
        if auth_employee.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return auth_employee.employee


require_admin = RoleChecker(["admin"])


async def get_logged_in_employee(
    auth_employee: AuthenticatedEmployee = Depends(get_authenticated_employee),
) -> EmployeePublicWithDepartmentAndTasks:
    return auth_employee.employee


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
