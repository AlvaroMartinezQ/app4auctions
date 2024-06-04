# os
from typing import Literal
import uuid

# Third party
from fastapi import APIRouter, Depends, status

# Local
from utils.database_context import Session
from app_auth.schemas import UserGet
from app_auth.encrypt import get_current_active_user
from app_wallet.schemas import UserWallets
from app_wallet.controller import WalletController


router = APIRouter()


@router.get(
    "/",
    response_model=UserWallets,
    status_code=status.HTTP_200_OK,
    summary="Get your virtual wallets",
)
async def get_wallet(current_user: "UserGet" = Depends(get_current_active_user)):
    """Get all of your virtual wallets

    - Requires the user to be logged in
    """
    with Session() as db:
        return WalletController(session=db).get(user=current_user)


@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new virtual wallet",
)
async def post_wallet(
    currency: Literal["euro", "pound", "dollar"],
    ammount: float,
    current_user: "UserGet" = Depends(get_current_active_user),
):
    """Create a new wallet

    Fields:
    - Currency as literal `euro, pound, dollar`
    - Ammount of money to be added to your new wallet, `float`
    """
    with Session() as db:
        return WalletController(session=db).post(
            currency=currency, ammount=ammount, user=current_user
        )


@router.put(
    "/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update a virtual wallet | Add more money to it",
)
async def put_wallet(
    wallet_id: uuid.UUID,
    ammount: float,
    current_user: "UserGet" = Depends(get_current_active_user),
):
    """Update a wallet you own by its UUID and the ammount you desire"""
    with Session() as db:
        return WalletController(session=db).put(
            wallet_id=wallet_id, ammount=ammount, user=current_user
        )


@router.delete(
    "/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete a virtual wallet",
)
async def put_wallet(
    wallet_id: uuid.UUID, current_user: "UserGet" = Depends(get_current_active_user)
):
    """Delete a virtual wallet you own"""
    with Session() as db:
        return WalletController(session=db).delete(
            wallet_id=wallet_id, user=current_user
        )
