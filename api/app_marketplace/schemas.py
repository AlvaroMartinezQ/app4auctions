import datetime
from enum import Enum
from typing import Literal, Optional, List

from pydantic import UUID4, PositiveInt

from utils.orm import OrmModel
from app_auth.schemas import UserGet


class BidPost(OrmModel):
    offer_ammount: float


class BidGet(BidPost):
    id: UUID4
    creation_date: datetime.datetime


class BidGetWUser(BidGet):
    user: UserGet


class AuctionPost(OrmModel):
    init_price: Optional[PositiveInt]
    price_currency: Literal["euro", "pound", "dollar"]
    start_date: datetime.datetime
    finish_date: datetime.datetime
    title: str
    description: str
    tags: str


class AuctionGet(AuctionPost):
    id: UUID4
    creation_date: datetime.datetime
    highest_offer: float | None
    bids: list[BidGet]


class AuctionWSimilarity(OrmModel):
    auction: AuctionGet
    similarity: float


class AuctionGetWUser(AuctionGet):
    user: UserGet


class AuctionGetList(OrmModel):
    auctions: List[AuctionGet]


class AuctionGetListFilterTFIDF(OrmModel):
    auctions: List[AuctionWSimilarity]


class AuctionGetListFiltersvm(OrmModel):
    auctions: List[AuctionGet]


class AuctionGetListFilterlsi(OrmModel):
    auctions: List[AuctionGet]


class BidGetList(OrmModel):
    bids: List[BidGet]


class FilterMethods(str, Enum):
    tfidf = "tfidf"
    lsi = "lsi"
    bayes = "bayes"
    svm = "svm"


class BuyProcess(OrmModel):
    id: UUID4
    seller_id: UUID4
    buyer_id: UUID4
    auction_id: UUID4
    creation_date: datetime.datetime


class ProcessList(OrmModel):
    processes: list[BuyProcess]
