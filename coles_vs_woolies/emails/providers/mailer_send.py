import logging
import os

from mailersend import emails

from ...utils.wednesday import get_week_of_month

_logger = logging.getLogger(__name__)


class MailerSend:
    @staticmethod
    def send(email_html: str, to_addrs: list[str], from_addr: str):
        """
        Send an email with MailerSend.
        :param email_html: email html template or file path to template.
        :param to_addrs: recipients' email address.
        :param from_addr: sender's email address.
        :return:
        """
        # Initialise MailerSend email
        if (mailersend_api_key := os.getenv("MAILERSEND_API_KEY")) is None:
            raise ValueError("MailerSend API Key not provided")
        mailer = emails.NewEmail(mailersend_api_key)

        # Define an empty dict to populate with mail values
        mail_body = {}
        mailer.set_mail_from({"name": "Coles vs. Woolies", "email": from_addr}, mail_body)
        mailer.set_reply_to([{"name": "no-reply", "email": from_addr}], mail_body)
        mailer.set_subject(get_week_of_month(), mail_body)

        # Recipients
        if len(to_addrs) > 1:
            mailer.set_mail_to([{"email": from_addr}], mail_body)
            recipients = [{"email": address} for address in to_addrs]
            mail_body["bcc"] = recipients
        else:
            mailer.set_mail_to([{"email": to_addrs[0]}], mail_body)

        # Email content
        mailer.set_html_content(email_html, mail_body)

        # Send email
        response = mailer.send(mail_body)
        if not response.startswith("202"):
            _logger.debug(response)
            raise ValueError("expected 202 response from MailerSend API")
