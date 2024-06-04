# os
from typing import List

# Third party
from pydantic import UUID4

# Local
from utils.orm import OrmModel


class UserWallet(OrmModel):
    id: UUID4
    ammount: float
    currency: str


class UserWallets(OrmModel):
    wallets: List[UserWallet]
