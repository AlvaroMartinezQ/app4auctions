import uuid
import typing

from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.sql.schema import Column
from sqlalchemy.types import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base

if typing.TYPE_CHECKING:
    from app_auth.models import GenericUser


class UserWallet(Base):
    __tablename__ = "market_wallet"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    ammount = Column(Float, unique=False, nullable=False, default=0.0)
    currency = Column(String(25), nullable=False, default="euro")
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("auth_base_user.id"),
        nullable=False,
        unique=False,
    )


class Auction(Base):
    __tablename__ = "market_auction"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    init_price = Column(
        Float(),
        unique=False,
        nullable=True,
    )
    price_currency = Column(
        String(10),
        unique=False,
        nullable=False,
    )
    creation_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        unique=False,
        nullable=False,
    )
    start_date = Column(
        DateTime(timezone=True),
        unique=False,
        nullable=False,
    )
    finish_date = Column(
        DateTime(timezone=True),
        unique=False,
        nullable=False,
    )
    title = Column(
        String(150),
        unique=False,
        nullable=False,
    )
    description = Column(
        String(300),
        unique=False,
        nullable=False,
    )
    tags = Column(
        String(300),
        unique=False,
        nullable=False,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("auth_base_user.id"),
        nullable=False,
        unique=False,
    )
    user: "GenericUser" = relationship(
        "GenericUser",
        single_parent=True,
        lazy=False,
    )

    bids: "list[Bid]" = relationship(
        "Bid",
        backref="auction",
        lazy=False,
        cascade="all,delete",
    )

    def highest_offer_data(self, id: bool = False) -> str | None:
        best = 0.0
        data = None
        for bid in self.bids:
            if bid.offer_ammount > best:
                best = bid.offer_ammount
                if id:
                    data = bid.user.id
                else:
                    data = bid.user.email
        return data

    @property
    def highest_offer(self) -> float | None:
        best = 0.0
        for bid in self.bids:
            if bid.offer_ammount > best:
                best = bid.offer_ammount
        return best if best > 0 else None

    @property
    def highest_offer_user(self) -> str | None:
        return self.highest_offer_data(id=False)

    @property
    def highest_offer_uid(self) -> str | None:
        return self.highest_offer_data(id=True)


class Bid(Base):
    __tablename__ = "market_bid"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    offer_ammount = Column(
        Float(),
        unique=False,
        nullable=False,
    )
    creation_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        unique=False,
        nullable=False,
    )

    auction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("market_auction.id"),
        nullable=False,
        unique=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("auth_base_user.id"),
        nullable=False,
        unique=False,
    )
    user: "GenericUser" = relationship(
        "GenericUser",
        single_parent=True,
        lazy=False,
    )


class CeleryTask(Base):
    __tablename__ = "celery_task"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    task_type = Column(
        String(30),
        unique=False,
        nullable=False,
    )
    task_uuid = Column(
        String(50),
        unique=True,
        nullable=False,
    )
    auction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("market_auction.id"),
        nullable=False,
        unique=False,
    )


class BuyProcess(Base):
    __tablename__ = "market_buy_process"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    creation_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        unique=False,
        nullable=False,
    )
    auction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("market_auction.id"),
        nullable=False,
        unique=False,
    )
    seller_id = Column(
        UUID(as_uuid=True),
        ForeignKey("auth_base_user.id"),
        nullable=False,
        unique=False,
    )
    buyer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("auth_base_user.id"),
        nullable=False,
        unique=False,
    )
