import json
import datetime
from pathlib import Path
from loguru import logger

from app_auth.encrypt import pwd_context
from utils.database_context import Session
from app_marketplace.models import Auction
from app_auth.models import GenericUser
from app_marketplace.models import UserWallet


FILES = {"users": "user.json", "wallets": "wallets.json", "auctions": "auctions.json"}


def data_ingestion() -> None:
    PATH = Path(__file__).resolve().parent

    admin_id = None
    for key, file in FILES.items():
        file_path = str(PATH) + "/" + file

        logger.warning(f"Ingesting data for file: {file_path}")
        with open(file=file_path) as f:
            data = json.load(f)

        with Session() as db:
            match key:
                case "users":
                    logger.info("Inserting admin user...")
                    test_user = GenericUser(**data)
                    test_user.password = pwd_context.hash(test_user.password)
                    test_user.active_notifications = True
                    test_user.active_account = True
                    test_user.is_admin = True
                    db.add(test_user)
                    db.commit()
                    admin_id = test_user.id
                case "wallets":
                    logger.info("Inserting wallets")
                    for entry in data["schemas"]:
                        test_wallet = UserWallet(**entry)
                        test_wallet.user_id = admin_id
                        db.add(test_wallet)
                        db.commit()
                case "auctions":
                    logger.info("Inserting auctions")
                    for entry in data["schemas"]:
                        test_auction = Auction(**entry)
                        test_auction.start_date = datetime.datetime.now(
                            datetime.timezone.utc
                        )
                        test_auction.user_id = admin_id
                        with Session() as db:
                            db.add(test_auction)
                            db.commit()
                case _:
                    pass
        logger.info("-- DONE")
