# os
import uuid

# Third party
from sqlalchemy import String, Boolean
from sqlalchemy.sql.schema import Column
from sqlalchemy.types import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Local
from database import Base
from utils.database_context import Session
from app_marketplace.models import Auction, Bid, UserWallet


class GenericUser(Base):
    __tablename__ = "auth_base_user"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    email = Column(
        String(200),
        unique=True,
        nullable=False,
    )
    password = Column(String, nullable=False)
    personal_name = Column(
        String(100),
        unique=False,
        nullable=False,
    )
    personal_surname = Column(
        String(100),
        unique=False,
        nullable=False,
    )
    identification_number = Column(
        String(100),
        unique=True,
        nullable=False,
    )
    country = Column(
        String(100),
        unique=False,
        nullable=False,
    )
    address = Column(
        String(250),
        unique=False,
        nullable=False,
    )
    phone = Column(
        String(50),
        unique=False,
        nullable=False,
    )
    singup_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        unique=False,
        nullable=False,
    )
    last_login = Column(
        DateTime(timezone=True),
        unique=False,
        nullable=True,
    )
    interests = Column(
        String(500),
        unique=False,
        nullable=True,
    )
    active_notifications = Column(
        Boolean,
        default=True,
    )
    active_account = Column(
        Boolean,
        default=False,
    )
    is_admin = Column(
        Boolean,
        default=False,
    )
    pwd_reset_token = Column(String(10), nullable=True)

    wallets: "list[UserWallet]" = relationship(
        "UserWallet",
        backref="user",
        lazy=False,
        cascade="all,delete",
    )

    def __str__(self) -> str:
        return f"User {self.id}: {self.email}, {self.personal_name}"

    @property
    def n_auctions(self) -> int:
        with Session() as db:
            return db.query(Auction).filter(Auction.user_id == self.id).count()

    @property
    def n_bids(self) -> int:
        with Session() as db:
            return db.query(Bid).filter(Bid.user_id == self.id).count()
