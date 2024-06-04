import uuid

from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from utils.database_context import Session
from app_auth.schemas import (
    UserGet,
    UserNew,
    UserPut,
    Token,
    UserPWDChange,
    UserEmailChange,
)
from app_auth.controller import UserController, LoginController
from app_auth.encrypt import get_current_active_user
from app_mailer.mails import sing_up_mail


router = APIRouter()


# User routes
@router.get(
    "/",
    response_model=UserGet,
    status_code=status.HTTP_200_OK,
    summary="Get your user data",
)
async def get_user(
    current_user: UserGet = Depends(get_current_active_user),
):
    retreived_user = UserController().get(current_user)

    return retreived_user


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a new user")
async def post_user(form_data: UserNew, background_task: BackgroundTasks):
    """Create a new user from the `UserNew` schema

    Requires:

        - :param: UserNew data

    Returns:

        - :value: HTTP code 201 CREATED or 422 UNPROCESSABLE ENTITY
    """
    with Session() as db:
        user_email, user_id = UserController(session=db).post(new_user=form_data)
        background_task.add_task(sing_up_mail, user_email, user_id)
        return {"status": "User created successfully"}


@router.put("/", status_code=status.HTTP_200_OK, summary="Update your user fields")
async def put_user(
    form_data: UserPut,
    current_user: UserGet = Depends(get_current_active_user),
):
    with Session() as db:
        UserController(session=db).put(user=form_data, user_id=current_user.id)
        return {"status": "User updated successfully"}


@router.delete("/", status_code=status.HTTP_200_OK, summary="Delete your user")
async def delete_user(current_user: UserGet = Depends(get_current_active_user)):
    with Session() as db:
        UserController(session=db).delete(current_user)
        return {"status": "User deleted successfully"}


# Activate
@router.get(
    "/activate/{user_uuid}/",
    status_code=status.HTTP_200_OK,
    summary="Activate your user",
)
async def activate_user(user_uuid: uuid.UUID):
    with Session() as db:
        UserController(session=db).activate_user(user_uuid=user_uuid)
        return {
            "status": "User activated successfully, you can now login into your account"
        }


# Login route
@router.post(
    "/login", response_model=Token, summary="Login with credentials: email & password"
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session() as db:
        return LoginController(db).authenticate_user(
            # Cannot change the 'OAuth2PasswordRequestForm' form data
            # so form_data.username stands for the user email
            user_email=form_data.username,
            password=form_data.password,
        )


# Change email route
@router.post("/email-change/", summary="Change a user email")
async def change_email(
    data: UserEmailChange,
    current_user: UserGet = Depends(get_current_active_user),
):
    with Session() as db:
        LoginController(session=db).email_change(data.old_email, data.new_email)
        return JSONResponse(content={"status": "Updated email"}, status_code=200)


# Change password route
@router.post("/password-change/", summary="Change a user password")
async def change_password(
    data: UserPWDChange,
    current_user: UserGet = Depends(get_current_active_user),
):
    with Session() as db:
        LoginController(session=db).password_change(
            data.old_pwd, data.new_pwd, data.new_pwd_repeated, current_user
        )
        return JSONResponse(content={"status": "Updated password"}, status_code=200)


# Forget password route
@router.post(
    "/password-reset/", summary="Send an email to change your password based on a code"
)
async def reset_password(
    email: str = None, email_token: str = None, new_password: str = None
):
    with Session() as db:
        return LoginController(session=db).password_reset(
            email=email, token=email_token, new_password=new_password
        )
