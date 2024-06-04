import typing
import datetime
from uuid import UUID
import pytz

from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger

from utils.database_context import Session as db
from app_auth.schemas import UserGet
from app_marketplace.models import Auction, Bid, UserWallet
from app_marketplace.schemas import (
    AuctionGetList,
    AuctionPost,
    AuctionGet,
    BidPost,
    BidGetList,
)
from app_marketplace.errors import (
    NotOwnedAuction,
    AuctionStarted,
    AuctionNotStarted,
    AuctionFinished,
    BadDates,
    NotFoudnAuction,
    BadAmmount,
    AuctionTimeInvalid,
    NotFoudnBid,
    WalletNotFound,
    MoneyNotEnoguh,
)
from app_marketplace.celery_creator import CeleryCreator
from app_ws.marketplace_ws import new_auction, new_bid
from app_mailer.mails import send_mail_new_bid

if typing.TYPE_CHECKING:
    from sqlalchemy.orm.session import Session as SQLSession


LOCAL_TZ = pytz.timezone("Europe/Madrid")


class InitController:
    def __init__(self, session: "db" = None) -> None:
        if session:
            self.session: "SQLSession" = session


class AuctionController(InitController):
    """Auction controller"""

    def __init__(self, session: "db" = None) -> None:
        super().__init__(session)

    def get(self, page: int, limit: int) -> "AuctionGetList":
        """Get active auctions"""

        now = datetime.datetime.now()
        result = AuctionGetList(
            auctions=(
                self.session.query(Auction)
                .filter(
                    Auction.start_date <= now,
                    Auction.finish_date > now,
                )
                .offset((page - 1) * limit)
                .limit(limit)
                .all()
            )
        )

        return result

    def get_auction(self, auction_id: UUID) -> "AuctionGet":
        """Get auction by UUID"""

        auction: Auction = (
            self.session.query(Auction).filter(Auction.id == auction_id).first()
        )

        if auction:
            return auction
        raise NotFoudnAuction(auction_id=auction_id)

    def post(
        self,
        auction_data: "AuctionPost",
        user: "UserGet",
    ) -> bool:
        """Create a new auction"""

        self.__validate_dates(
            finish_date=auction_data.finish_date, start_date=auction_data.start_date
        )

        now = (
            LOCAL_TZ.localize(datetime.datetime.now())
            .replace(tzinfo=pytz.utc)
            .astimezone(LOCAL_TZ)
        )
        auction_start_date = auction_data.start_date.replace(
            tzinfo=pytz.utc
        ).astimezone(LOCAL_TZ)

        if auction_start_date < now:
            # Auction start time cannot be < now()
            raise AuctionTimeInvalid()

        auction_data.tags = self.__clean_tags(tags=auction_data.tags)
        auction_dict = dict(auction_data)
        auction_obj = Auction(**auction_dict)
        auction_obj.user_id = user.id
        self.session.add(auction_obj)
        self.session.commit()

        c_creator = CeleryCreator()
        c_creator.add_tasks(session=self.session, auction=auction_obj, update=False)

        return True

    def update_active_clients(
        self,
        auction_id: UUID,
        background_tasks: BackgroundTasks,
    ) -> None:
        """Update all connected clients when an auction starts"""
        try:
            background_tasks.add_task(new_auction, auction_id)
        except Exception as e:
            logger.error(
                f"There was an exception on the auction controller (marketplace ws):\n{str(e)}"
            )

    def put(
        self,
        auction_id: UUID,
        auction_data: "AuctionPost",
        user: "UserGet",
    ) -> bool:
        """Update an auction"""
        self.__validate_dates(
            finish_date=auction_data.finish_date, start_date=auction_data.start_date
        )

        # Allow update only if the user owns the Auction and it hasn't started yet
        auction: Auction = (
            self.session.query(Auction)
            .filter(Auction.id == auction_id, Auction.user_id == user.id)
            .first()
        )

        # If the auction exists
        if auction:
            now = (
                LOCAL_TZ.localize(datetime.datetime.now())
                .replace(tzinfo=pytz.utc)
                .astimezone(LOCAL_TZ)
            )

            # If the auction has not yet started
            if auction.start_date > now:
                auction_start_date = auction_data.start_date.replace(
                    tzinfo=pytz.utc
                ).astimezone(LOCAL_TZ)

                # If the passed time is valid
                if auction_start_date > now:
                    auction_dict = dict(auction_data)

                    for key, value in auction_dict.items():
                        setattr(auction, key, value)

                    self.session.add(auction)
                    self.session.commit()

                    c_creator = CeleryCreator()
                    c_creator.add_tasks(
                        session=self.session, auction=auction, update=True
                    )
                    return True
                else:
                    raise AuctionTimeInvalid()
            else:
                raise AuctionStarted()
        else:
            raise NotOwnedAuction()

    def delete(
        self,
        auction_id: UUID,
        user: "UserGet",
    ) -> bool:
        """Delete an auction, only allowed if no bids have been performed"""

        auction: Auction = (
            self.session.query(Auction)
            .filter(Auction.id == auction_id, Auction.user_id == user.id)
            .first()
        )

        if auction and len(auction.bids) == 0:
            self.session.delete(auction)
            self.session.commit()
            return True
        elif not auction:
            raise NotFoudnAuction(auction_id=auction_id)
        else:
            raise AuctionStarted()

    def get_user_auctions(self, user: "UserGet") -> "AuctionGetList":
        """Get user auctions"""

        data = AuctionGetList(
            auctions=self.session.query(Auction)
            .filter(Auction.user_id == user.id)
            .all()
        )

        return data

    def user_can_edit(self, auction_id: UUID, user: "UserGet") -> bool:
        auction: Auction = (
            self.session.query(Auction)
            .filter((Auction.id == auction_id) & (Auction.user_id == user.id))
            .first()
        )

        if auction:
            return True
        return False

    def __validate_dates(self, finish_date: datetime, start_date: datetime) -> bool:
        if start_date >= finish_date:
            raise BadDates()

    def __clean_tags(self, tags: str) -> str:
        """Clean passed tags on Auction creation"""

        arr = tags.split(" ")
        cleaned_tags = ""
        for entry in arr:
            letters = False
            for l in entry:
                if l.isalpha():
                    letters = True
            if letters:
                cleaned_tags += "".join(filter(str.isalpha, entry))
                cleaned_tags += " "

        return cleaned_tags.strip()


class BidController(InitController):
    """Bid controller"""

    def __init__(self, session: "db" = None) -> None:
        super().__init__(session)

    def get(self, auction_id: UUID, user: "UserGet") -> "Bid":
        """Get a user bid for a given auction"""
        auction: Auction = (
            self.session.query(Auction).filter(Auction.id == auction_id).first()
        )

        if auction:
            for bid in auction.bids:
                if bid.user.email == user.email:
                    return bid
        return None

    def get_auction(self, bid_id: UUID) -> Auction:
        """Get an auction with a bid ID"""
        bid: Bid = self.session.query(Bid).filter(Bid.id == bid_id).first()
        if bid is not None:
            auction: Auction = (
                self.session.query(Auction).filter(Auction.id == bid.auction_id).first()
            )
            if auction is not None:
                return auction
            raise NotFoudnAuction(bid.auction_id)
        raise NotFoudnBid(bid_id)

    def post(
        self,
        bid_data: "BidPost",
        auction_id: UUID,
        background_tasks: BackgroundTasks,
        user: "UserGet",
    ) -> bool:
        """Create a new bid for an existing auction"""

        auction: Auction = AuctionController(session=self.session).get_auction(
            auction_id=auction_id
        )
        user_wallet = self.__get_user_wallet(user, auction.price_currency)

        if self.__validate_bid(
            auction=auction,
            offer_ammount=bid_data.offer_ammount,
            user=user,
            background_tasks=background_tasks,
        ):
            return True

        # Create the bid
        bid_dict = dict(bid_data)
        bid_obj = Bid(**bid_dict)
        bid_obj.auction_id = auction.id
        bid_obj.user_id = user.id

        # Check if wallet has enough money
        if user_wallet.ammount < bid_obj.offer_ammount:
            raise MoneyNotEnoguh()
        user_wallet.ammount -= bid_obj.offer_ammount

        self.session.add(bid_obj)
        self.session.add(user_wallet)
        self.session.commit()

        # Send data to the market_ws-bids
        try:
            background_tasks.add_task(new_bid, auction_id, bid_obj.id)
        except Exception as e:
            logger.error(
                f"There was an exception on the marketplace ws (bids):\n{str(e)}"
            )

        background_tasks.add_task(
            send_mail_new_bid,
            auction.user.email,
            bid_obj.user.email,
            bid_obj.id,
            bid_obj.offer_ammount,
            auction_id,
        )

        return True

    def put(
        self,
        bid_data: "BidPost",
        auction_id: UUID,
        user: "UserGet",
        background_tasks: BackgroundTasks,
    ) -> bool:
        """Update a bid"""
        auction = AuctionController(session=self.session).get_auction(
            auction_id=auction_id
        )

        if self.__validate_bid(
            auction=auction,
            offer_ammount=bid_data.offer_ammount,
            user=user,
            background_tasks=background_tasks,
        ):
            return True

        return JSONResponse(
            status_code=400,
            content={"detail": "Bid or auction not found"},
        )

    def delete():
        """Once a bid has been performed, it cannot be undone!"""
        return JSONResponse(
            status_code=405,
            content={"detail": "You cannot delete your bid once performed!"},
        )

    def get_user_bids(self, user: "UserGet") -> "BidGetList":
        """Get user bids"""
        data = BidGetList(
            bids=self.session.query(Bid).filter(Bid.user_id == user.id).all()
        )

        return data

    def __update_bid(
        self,
        offer_ammount: float,
        bid: "Bid",
        auction: "Auction",
        user: "UserGet",
        background_tasks: BackgroundTasks,
    ) -> bool:
        user_wallet = self.__get_user_wallet(user, auction.price_currency)
        if user_wallet.ammount < offer_ammount:
            raise MoneyNotEnoguh()
        user_wallet.ammount -= offer_ammount - bid.offer_ammount
        bid.offer_ammount = offer_ammount
        self.session.add(bid)
        self.session.add(user_wallet)
        self.session.commit()

        self.__ws_bid_data(auction.id, bid.id, background_tasks)

        return True

    def __validate_bid(
        self,
        auction: "Auction",
        offer_ammount: float,
        user: "UserGet",
        background_tasks: BackgroundTasks,
    ) -> bool:
        """Validate the bid data"""
        # 1 hour offset
        now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            hours=2
        )  # Depends on summer time

        if auction.finish_date < now:
            # If the auction has finished return an error
            raise AuctionFinished()
        if auction.start_date > now:
            # If the auction has not started return an error
            raise AuctionNotStarted()

        if not auction.highest_offer:
            if auction.init_price != None and auction.init_price > offer_ammount:
                # If there're no bids, the auction has an init price and that price is bigger
                # than the ammount offered return an error
                raise BadAmmount(
                    auction_price=auction.init_price, offer_price=offer_ammount
                )
        else:
            if auction.highest_offer > offer_ammount:
                # If the offered ammount is smaller than the highest offer of the auction
                # return an error
                raise BadAmmount(
                    auction_price=auction.highest_offer, offer_price=offer_ammount
                )

        for bid in auction.bids:
            if bid.user.id == user.id:
                return self.__update_bid(
                    offer_ammount=offer_ammount,
                    bid=bid,
                    auction=auction,
                    user=user,
                    background_tasks=background_tasks,
                )

    def __ws_bid_data(
        self,
        auction_id,
        bid_id,
        background_tasks: BackgroundTasks,
    ) -> None:
        try:
            background_tasks.add_task(new_bid, auction_id, bid_id)
        except Exception as e:
            logger.error(
                f"There was an exception on the marketplace ws (bids):\n{str(e)}"
            )

    def __get_user_wallet(self, user: "UserGet", currency: str) -> "UserWallet":
        """Get the requested user wallet based on the requested currency"""
        user_wallet = (
            self.session.query(UserWallet)
            .filter(UserWallet.user_id == user.id, UserWallet.currency == currency)
            .first()
        )
        if user_wallet:
            return user_wallet
        raise WalletNotFound()
