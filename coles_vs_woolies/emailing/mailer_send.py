import datetime
import os
from typing import List

from dotenv import load_dotenv, find_dotenv
from mailersend import emails


def send(email_html: str, to_addrs: List[str], from_addr: str, mailersend_api_key: str = None):
    """
    Send an email with MailerSend.
    :param email_html: email html template or file path to template.
    :param to_addrs: recipients' email address.
    :param from_addr: sender's email address.
    :param mailersend_api_key: API key for MailerSend. If not given, pulled from env-vars.
    :return:
    """
    # If file path, load email html template
    if os.path.isfile(email_html):
        with open(email_html, 'r', encoding='utf-8') as fp:
            email_html = fp.read()

    # Setup MailerSend email
    if mailersend_api_key is None:
        load_dotenv(dotenv_path=find_dotenv())
        mailersend_api_key = os.getenv('MAILERSEND_API_KEY')
        if mailersend_api_key is None:
            raise ValueError("MailerSend API Key not provided")
    mailer = emails.NewEmail(mailersend_api_key)

    # Define an empty dict to populate with mail values
    mail_body = {}
    week_of_year = datetime.datetime.now().isocalendar().week
    mailer.set_mail_from({"name": "Coles vs. Woolies", "email": from_addr}, mail_body)
    mailer.set_reply_to([{"name": "no-reply", "email": from_addr}], mail_body)
    mailer.set_subject(f"Wk{week_of_year} Special prices for special items", mail_body)

    # Recipients
    recipients = [{"email": address} for address in to_addrs]
    mailer.set_mail_to(recipients, mail_body)

    # Email content
    mailer.set_html_content(email_html, mail_body)

    # Send email
    response = mailer.send(mail_body)
    if not response.startswith('202'):
        print(response)
        raise ValueError(f"expected 202 response from MailerSend API")
    else:
        print(f"Emails sent: {len(to_addrs)}")


if __name__ == '__main__':
    import fire

    fire.Fire(send)
