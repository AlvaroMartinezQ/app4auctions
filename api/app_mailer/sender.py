import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPServerDisconnected

from jinja2 import TemplateNotFound, Template
from loguru import logger

from main import templates


def send_mail(
    template: str,
    email_data: dict,
    subject: str,
    receiver: str,
) -> bool:
    """Send a HTML email in the name of App4Auctions

    - Data:

        - @param template: the name of the requested html template to send to the user
        - @param email_data: the data as a dict to populate the email with
        - @param subject: the title of the email
        - @param receiver: the user to send the email to
    """
    if os.getenv("MAILER"):
        try:
            template: Template = templates.get_template(template)
            html = template.render(email_data)
        except TemplateNotFound as e:
            logger.error(f"Template not found: {str(e)}")
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = os.getenv("MAILER_USER")
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
