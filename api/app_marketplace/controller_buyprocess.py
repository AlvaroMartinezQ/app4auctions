from utils.database_context import Session as db
from app_marketplace.controller import InitController
from app_auth.schemas import UserGet
from app_marketplace.schemas import ProcessList
from app_marketplace.models import BuyProcess


class BuyProcessController(InitController):
    """Buy Process controller"""

    def __init__(self, session: "db" = None) -> None:
        super().__init__(session)

    def get_buyprocess(self, user: "UserGet") -> ProcessList:
        """Get all existing BUY operations made by a user"""
        return ProcessList(
            processes=self.session.query(BuyProcess)
            .filter(BuyProcess.buyer_id == user.id)
            .all()
        )

    def get_sellprocess(self, user: "UserGet") -> ProcessList:
        """Get all existing SELL operations made by a user"""
        return ProcessList(
            processes=self.session.query(BuyProcess)
            .filter(BuyProcess.seller_id == user.id)
            .all()
        )
