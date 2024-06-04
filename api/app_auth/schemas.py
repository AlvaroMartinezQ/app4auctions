# os
import datetime
from typing import Optional

# Third party
from pydantic import BaseModel, UUID4

# Local
from utils.orm import OrmModel


# User wallet - object defined in marketplace models
class UserWallet(OrmModel):
    id: UUID4
    ammount: float
    currency: str


# User schemas - as: User<action>
class UserGet(OrmModel):
    id: Optional[UUID4]
    personal_name: str
    personal_surname: str | None = None
    singup_date: datetime.datetime
    last_login: datetime.datetime
    email: str | None = None
    active_account: bool | None = None
    n_auctions: int
    n_bids: int
    address: str
    phone: str
    identification_number: str
    country: str
    wallets: list["UserWallet"]


class UserPut(OrmModel):
    identification_number: str
    personal_name: str
    personal_surname: str
    country: str
    address: str
    phone: str


class UserNew(UserPut):  # Extend the update model
    email: str
    password: str


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# User email change
class UserEmailChange(BaseModel):
    old_email: str
    new_email: str


# User password change
class UserPWDChange(BaseModel):
    old_pwd: str
    new_pwd: str
    new_pwd_repeated: str
