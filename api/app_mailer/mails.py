import os
from uuid import UUID
import logging

from app_mailer.sender import send_mail

from loguru import logger


def sing_up_mail(client_email: str, client_id: UUID) -> None:
    """Send a welcome email to a new user

    - Data:

        - @param client_email: the email of the user
        - @param client_id: the identifier of the user - required for activation
    """
    logger.info(f"New account on the web {client_email} - Sending welcome email")
    if os.getenv("ACTIVATE_ACC_URL"):
        activation_link = os.getenv("ACTIVATE_ACC_URL") + str(client_id)
    else:
        activation_link = f"http://localhost:5000/auth/user/activate/{client_id}/"

    if "MAILER" in os.environ:
        send_mail(
            template="welcome.html",
            email_data={"email": client_email, "link": activation_link},
            subject="Welcome to App4Auctions!",
            receiver=client_email,
        )
    else:
        logger.info(f"Activate user account: {client_id} via GET: {activation_link}")


def password_reset_email(client_email: str, client_token: str) -> None:
    if os.getenv("MAILER"):
        send_mail(
            template="password_reset.html",
            email_data={"email": client_email, "token": client_token},
            subject="Password reset",
            receiver=client_email,
        )
    else:
        logger.warning(f"Token for password reset {client_email}: {client_token}")


def send_mail_new_bid(
    receiver: str, creator: str, bid_id: UUID, price: float, auction_id: UUID
) -> None:
    """Send a bid performed email to the user of the auction and the user creator of the bid

    - Data:

        - @param receiver: the email of the user who owns/created the auction
        - @param creator: the email of the user who owns/created the bid
        - @param bid_id: the id of the bid
        - @param price: ammount offered in the bid
    """

    if os.getenv("MAILER"):
        if send_mail(
            template="bid_created.html",
            email_data={
                "title": "Bid received",
                "email": receiver,
                "text": f"you have received a bid for your auction! Price: {price}",
                "auction_id": auction_id,
            },
            subject="Bid received",
            receiver=receiver,  # User owner of the auction
        ) and send_mail(
            template="bid_created.html",
            email_data={
                "title": "Bid performed",
                "email": creator,
                "text": f"you have created a bid for an auction in our services! Price: {price}",
                "auction_id": auction_id,
            },
            subject="Bid created",
            receiver=creator,  # User creator of the bid
        ):
            return
    logging.warning(f"New bid created with id: {bid_id}")
