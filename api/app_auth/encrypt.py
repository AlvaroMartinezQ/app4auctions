# os
import os

# Third party
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

# Local
from app_auth.schemas import *
from utils.database_context import Session as SQLSession
from app_auth.models import GenericUser


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/user/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
        token_data = TokenData(username=user_email)

        with SQLSession() as db:
            user: GenericUser = (
                db.query(GenericUser)
                .filter(
                    GenericUser.email == token_data.username
                )  # token_data.username is the email
                .first()
            )

            if user is None:
                raise credentials_exception
            return user
    except JWTError:
        raise credentials_exception


async def get_current_active_user(current_user: UserGet = Depends(get_current_user)):
    if not current_user.active_account:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
