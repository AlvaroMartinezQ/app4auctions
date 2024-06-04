# os
import os
import typing
import uuid
import logging
import datetime
import random
import string
from datetime import timedelta

# Third party
from email_validator import validate_email, EmailNotValidError
from jose import jwt
from fastapi.responses import JSONResponse

# Local
from utils.database_context import Session as db
from app_auth.schemas import UserNew, UserGet, UserPut
from app_auth.models import GenericUser
from app_auth.errors import (
    UserDataExists,
    BadEmail,
    BadLoginParams,
    InactiveUser,
    NotFoundUser,
    PasswordsMatch,
)
from app_auth.enums import FilterType
from app_mailer.mails import password_reset_email

from app_auth.encrypt import pwd_context

if typing.TYPE_CHECKING:
    from sqlalchemy.orm.session import Session as SQLSession


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


class UserController:
    def __init__(self, session: "db" = None) -> None:
        if session:
            self.session: "SQLSession" = session

    def get(self, user: "UserGet") -> "UserGet":
        return user

    def post(self, new_user: "UserNew") -> uuid:
        self._valid_email(new_user.email)

        if self._ensure_creation(
            email=new_user.email, identification_number=new_user.identification_number
        ):
            user_dict = dict(new_user)
            user_obj = GenericUser(**user_dict)

            self.session.add(user_obj)

            user_obj.password = pwd_context.hash(user_obj.password)

            self.session.commit()

            return user_obj.email, user_obj.id

    def put(self, user: "UserPut", user_id: uuid) -> None:
        user_obj: GenericUser = (
            self.session.query(GenericUser).filter(GenericUser.id == user_id).first()
        )

        if user_obj:
            for key, value in dict(user).items():
                setattr(user_obj, key, value)

            self.session.add(user_obj)
            self.session.commit()

    def delete(self, user: "UserGet") -> bool:
        user_obj: GenericUser = (
            self.session.query(GenericUser)
            .filter(GenericUser.email == user.email)
            .first()
        )

        if user_obj:
            # Will just suspend the account
            user_obj.active_account = False
            self.session.add(user_obj)
            self.session.commit()

            return True

        raise NotFoundUser()

    def activate_user(self, user_uuid: uuid.UUID) -> bool:
        user_obj: GenericUser = (
            self.session.query(GenericUser).filter(GenericUser.id == user_uuid).first()
        )

        if user_obj:
            user_obj.active_account = True
            self.session.add(user_obj)
            self.session.commit()

            return True

        raise NotFoundUser()

    def _valid_email(self, email: str) -> bool:
        try:
            validate_email(email, check_deliverability=True)
        except EmailNotValidError as _:
            logging.warn(f"Bad email registered on singup: {email}")
            raise BadEmail(email=email)

    def _ensure_creation(self, email: str, identification_number: str) -> bool:
        """Validate user creation"""

        if self.__filter(field=email, type=FilterType.EMAIL):
            # Email has to be unique
            raise UserDataExists(name=email, type=FilterType.EMAIL)
        if self.__filter(field=identification_number, type=FilterType.USER_ID_NUMBER):
            # User identification number has to be unique
            raise UserDataExists(
                name=identification_number, type=FilterType.USER_ID_NUMBER
            )

        return True

    def __filter(self, field: str, type: "FilterType") -> bool:
        match type:
            case FilterType.EMAIL:
                user = (
                    self.session.query(GenericUser)
                    .filter(GenericUser.email == field)
                    .first()
                )
                return True if user is not None else False
            case FilterType.USER_ID_NUMBER:
                user = (
                    self.session.query(GenericUser)
                    .filter(GenericUser.identification_number == field)
                    .first()
                )
                return True if user is not None else False
            case _:
                logging.info(msg="Bad params in UserController.__filter()")


class LoginController:
    def __init__(self, session: "db" = None) -> None:
        if session:
            self.session: "SQLSession" = session

    def authenticate_user(self, user_email: str, password: str):
        user = self._search_user(user_email=user_email)
        if user:
            if self._password_validation(password=password, user=user):
                if not user.active_account:
                    raise InactiveUser()
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

                access_token = self._create_access_token(
                    data={"sub": user.email}, expires_delta=access_token_expires
                )

                user.last_login = datetime.datetime.now()
                self.session.add(user)
                self.session.commit()

                return {"access_token": access_token, "token_type": "bearer"}
        self._bad_params()

    def email_change(self, old_email: str, new_email: str) -> None:
        user = self._search_user(old_email)
        user.email = new_email
        self.session.add(user)
        self.session.commit()

    def password_change(
        self, old_pwd: str, new_pwd: str, new_pwd_repeated: str, current_user: UserGet
    ) -> None:
        if new_pwd == new_pwd_repeated:
            user = self._search_user(current_user.email)
            if user and self._password_validation(old_pwd, user):
                # Perform the change (hash password)
                user.password = pwd_context.hash(new_pwd)
                self.session.add(user)
                self.session.commit()
            else:
                raise BadLoginParams()
        else:
            raise PasswordsMatch()

    def password_reset(
        self, email: str = None, token: str = None, new_password: str = None
    ):
        user = self._search_user(email)
        if user:
            if email and not token:
                token = "".join(
                    random.choices(
                        string.ascii_uppercase + string.ascii_lowercase + string.digits,
                        k=6,
                    )
                )
                user.pwd_reset_token = token
                self.session.add(user)
                password_reset_email(client_email=email, client_token=token)
                self.session.commit()
            elif email and token:
                if token == user.pwd_reset_token:
                    user.password = pwd_context.hash(new_password)
                    user.pwd_reset_token = ""
                    self.session.add(user)
                    self.session.commit()
                    return JSONResponse(
                        status_code=200,
                        content={"detail": "Your password has been updated"},
                    )
                return JSONResponse(
                    status_code=400,
                    content={"detail": "There was an error processing your request"},
                )

    def _create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta
        else:
            expire = datetime.datetime.utcnow() + timedelta(
                minutes=10
            )  # 10 minute default

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    def _search_user(self, user_email: str) -> GenericUser:
        return (
            self.session.query(GenericUser)
            .filter(GenericUser.email == user_email)
            .first()
        )

    def _password_validation(self, password: str, user: GenericUser):
        return pwd_context.verify(password, user.password)

    def _bad_params(self) -> None:
        raise BadLoginParams()
