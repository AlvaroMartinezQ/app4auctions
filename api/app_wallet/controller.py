# os
from uuid import UUID

# Third party
from fastapi.responses import JSONResponse

# Local
from utils.database_context import Session as db
from app_auth.schemas import UserGet
from app_marketplace.models import UserWallet
from app_marketplace.controller import InitController
from app_wallet.schemas import UserWallets


class WalletController(InitController):
    def __init__(self, session: "db" = None) -> None:
        super().__init__(session)

    def get(self, user: "UserGet") -> "UserWallets":
        """Get all wallets owned by a user"""

        return UserWallets(
            wallets=(
                self.session.query(UserWallet)
                .filter(UserWallet.user_id == user.id)
                .all()
            )
        )

    def post(self, currency: str, ammount: float, user: "UserGet") -> dict:
        """Create a new wallet for a user"""

        for wallet in user.wallets:
            if wallet.currency == currency:
                wallet.ammount += ammount
                self.session.add(wallet)
                self.session.commit()

                return {
                    "status": f"You already had a wallet with currency: {currency}. Its ammount value has been updated"
                }

        new_wallet = UserWallet(ammount=ammount, currency=currency, user_id=user.id)

        self.session.add(new_wallet)
        self.session.commit()

        return {"status": "Wallet created successfully"}

    def put(self, wallet_id: UUID, ammount: float, user: "UserGet") -> dict:
        """Update the ammount of money in a virtual wallet"""

        wallet: UserWallet = (
            self.session.query(UserWallet)
            .filter(UserWallet.id == wallet_id, UserWallet.user_id == user.id)
            .first()
        )

        if wallet:
            wallet.ammount += ammount
            self.session.add(wallet)
            self.session.commit()

            return {"status": "Ammount was added to your wallet"}
        return JSONResponse(
            status_code=400,
            content={"detail": "Wallet not found"},
        )

    def delete(self, wallet_id: UUID, user: "UserGet") -> dict:
        """Delete a virtual wallet"""

        wallet: UserWallet = (
            self.session.query(UserWallet)
            .filter(UserWallet.id == wallet_id, UserWallet.user_id == user.id)
            .first()
        )

        if wallet:
            self.session.delete(wallet)
            self.session.commit()
            return {"status": "Wallet deleted successfully"}
        return JSONResponse(
            status_code=400,
            content={"detail": "Wallet not found"},
        )
