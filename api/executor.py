import os
from pathlib import Path

# The celery executor
from celery import Celery

import requests

from loguru import logger

# SMTP and emails
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPServerDisconnected
from fastapi.templating import Jinja2Templates

# Templates
import jinja2
from jinja2 import TemplateNotFound

# Local dependencies - needed to query the database
from utils.database_context import Session
from app_marketplace.models import Auction, Bid, UserWallet, BuyProcess
from app_auth.models import GenericUser


# Same config as in main.py
DEBUG = False
if "DEBUG" in os.environ:
    DEBUG = True
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

if DEBUG:
    logger.warning(f"{__name__} - Running under DEBUG mode.")
    from utils.load_conf import LocalConfig

    LocalConfig.load(BASE_DIR=BASE_DIR)

    if None in [
        os.getenv("REDIS_PASSWORD"),
        os.getenv("REDIS_SERVER"),
        os.getenv("REDIS_PORT"),
    ]:
        raise Exception("Missing envvars to start the Celery executor.")


# The celery scheduler
app = Celery(
    "executor",
    broker=f"redis://:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_SERVER')}:{os.getenv('REDIS_PORT')}",
)

# Load config from the celeryconfig.py file
# app.config_from_object("celeryconfig")


# Send email function
def send_mail(
    template: str,
    email_data: dict,
    subject: str,
    receiver: str,
) -> bool:
    if os.getenv("MAILER"):
        try:
            template: jinja2.Template = templates.get_template(template)
            html = template.render(email_data)
        except TemplateNotFound as e:
            logger.error(f"Template not found: {str(e)}")
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = "App4Auctions"
        message["To"] = receiver
        message.attach(MIMEText(html, "html"))

        try:
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(
                os.getenv("MAILER_HOST"), os.getenv("MAILER_PORT"), context=context
            ) as mailer:
                mailer.login(os.getenv("MAILER_USER"), os.getenv("MAILER_PASSWORD"))
                mailer.sendmail(os.getenv("MAILER_USER"), receiver, message.as_string())
            return True
        except SMTPServerDisconnected as _:
            logger.warning("SMTP server disconnected?")
    return False


# ----------------
# Celery tasks


@app.task()
def send_auction(*args):
    """
    This function will call the backend server, to update the list of active auctions
    when the passed auction becomes as active (aka when it starts)
    """

    logger.info(f"Auction {args[0]} has started.")
    url = f"http://127.0.0.1:5000/market/auction-start/{args[0]}/"
    token_name = os.getenv("CELERY_TOKEN_NAME")
    token_value = os.getenv("CELERY_TOKEN_VALUE")
    headers = {token_name: token_value, "Content-Type": "application/json"}
    requests.post(url, headers=headers)
    logger.info(f"Auction {args[0]} was send to connected clients (if any)")


@app.task()
def end_auction(*args):
    """This function will select the winner for a given auction on the passed eta

    The function receives the UUID of an auction.
    It will:
        - Query the auction
        - Check if there are winners (best bidder)
            - Inform the user who created the auction it just finished (and if there are winners)
            - Inform the winner (if there is any)
    """

    logger.info(f"Auction {args[0]} finished. Processing final info.")
    with Session() as db:
        auction: Auction = db.query(Auction).filter(Auction.id == args[0]).first()

        if auction:
            creator_email = auction.user.email
            if auction.highest_offer_user:
                # Auction has at least a bid
                # Send email to both creator and winner
                bidder_email = auction.highest_offer_user
                send_mail(
                    "creator_auction_end.html",
                    email_data={
                        "header": "Your auction ended!",
                        "email": creator_email,
                        "auction_title": auction.title,
                        "text": " has a winner! Congratulations!",
                    },
                    subject="Your auction ended",
                    receiver=creator_email,
                )
                send_mail(
                    "bidder_auction_end.html",
                    email_data={
                        "header": "You won an auction!",
                        "email": bidder_email,
                        "auction_title": auction.title,
                        "text": f"Get in touch with the seller at: {creator_email}",
                    },
                    subject="Your auction ended",
                    receiver=creator_email,
                )
                # Create the buy process
                dp_d = {
                    "auction_id": auction.id,
                    "seller_id": auction.user.id,
                    "buyer_id": auction.highest_offer_uid,
                }
                bp = BuyProcess(**dp_d)
                db.add(bp)
                db.commit()
                # If there're more bids in the auction
                # ammounts have to be returned to the respective owners
                bids: list[Bid] = (
                    db.query(Bid).filter(Bid.auction_id == auction.id).all()
                )
                if len(bids) > 1:
                    for bid in bids:
                        if bid.user.email != bidder_email:
                            user_wallet: UserWallet = (
                                db.query(UserWallet)
                                .filter(
                                    UserWallet.user_id == bid.user_id,
                                    UserWallet.currency == auction.price_currency,
                                )
                                .first()
                            )
                            if user_wallet:
                                user_wallet.ammount += bid.offer_ammount
                                db.add(user_wallet)
                                db.commit()
                            else:
                                logger.error(
                                    f"Did not find a wallet to return {bid.user.email} the ammount of {bid.offer_ammount} {auction.price_currency}"
                                )
            else:
                # Send email only to creator - no bids received
                send_mail(
                    "creator_auction_end.html",
                    email_data={
                        "header": "Your auction ended!",
                        "email": creator_email,
                        "auction_title": auction.title,
                        "text": " sadly received no bids. Better luck next time!",
                    },
                    subject="Your auction ended",
                    receiver=creator_email,
                )
        else:
            logger.error(f"Passed auction ID {args[0]} to celery task does not exist.")


# End of celery tasks
# ----------------
