# os

# Third party
from fastapi import Request
from fastapi.responses import JSONResponse

# Local
from main import app
from app_auth.enums import FilterType


class UserDataExists(Exception):
    def __init__(self, name: str, type: "FilterType") -> None:
        self.type = type
        self.name = name
        super().__init__()


@app.exception_handler(UserDataExists)
async def taken_username(request: Request, exc: UserDataExists):
    match exc.type:
        case FilterType.USER_ID_NUMBER:
            msg = f"User identification number '{exc.name}' is already registered."
        case FilterType.EMAIL:
            msg = f"Email '{exc.name}' is already registered."

    return JSONResponse(
        status_code=400,
        content={"detail": msg},
    )


class BadEmail(Exception):
    def __init__(self, email: str) -> None:
        self.bad_email = email
        super().__init__()


@app.exception_handler(BadEmail)
async def bad_email(request: Request, exc: BadEmail):
    return JSONResponse(
        status_code=400,
        content={"detail": f"Non allowed email '{exc.bad_email}'"},
    )


class BadLoginParams(Exception):
    def __init__(self) -> None:
        super().__init__()


@app.exception_handler(BadLoginParams)
async def login_params_handler(request: Request, exc: BadLoginParams):
    return JSONResponse(
        status_code=400,
        content={"detail": "Incorrect username or password"},
        headers={"WWW-Authenticate": "Bearer"},
    )


class InactiveUser(Exception):
    def __init__(self) -> None:
        self.msg = "User is not active, please activate it first"
        super().__init__()


@app.exception_handler(InactiveUser)
async def bad_uuid(request: Request, exc: InactiveUser):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )


class NotFoundUser(Exception):
    def __init__(self) -> None:
        self.msg = "User not found"
        super().__init__()


@app.exception_handler(NotFoundUser)
async def bad_uuid(request: Request, exc: NotFoundUser):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )


class PasswordsMatch(Exception):
    def __init__(self) -> None:
        self.msg = "Passwords do not match!"
        super().__init__()


@app.exception_handler(PasswordsMatch)
async def bad_pwds(request: Request, exc: PasswordsMatch):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )
