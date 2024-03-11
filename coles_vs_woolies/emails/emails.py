import json
import logging
import os
import pathlib

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, EmailStr, parse_obj_as

from .. import merchants, search
from . import providers, templates

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

load_dotenv(dotenv_path=find_dotenv())


class EmailList(BaseModel):
    to_addr: EmailStr
    products: set[str]


def censor_email_addr(addr: str) -> str:
    prefix, domain = addr.split("@")
    return f'{prefix[:5].ljust(10, "*")}@{domain}'


def send_weekly_email(
    filepath: pathlib.Path,
    out_dir: pathlib.Path | None = None,
    dry_run: bool = False,
    verbose: bool = False,
):
    # Make output directory
    if out_dir:
        out_dir.mkdir(exist_ok=True)

    # Load requests from json
    with open(filepath, "r") as f:
        request_file = json.load(f)
    email_list: list[EmailList] = parse_obj_as(list[EmailList], request_file)

    for request in email_list:
        # Search for products
        product_offers: dict[str, list[merchants.ProductClass]] = {}
        bulk_search = search.BulkSearch(keywords=request.products)
        for product_search in bulk_search:
            name = product_search.keyword
            best_offers = product_search.im_feeling_lucky()
            if not len(best_offers):
                _logger.warning(f'no results for "{name}"')
                continue
            product_offers[name] = best_offers
        if not product_offers:
            _logger.error(f"no products found: {request.products}")
            return []

        # [dev] display products
        if verbose:
            bulk_search.display(isolate_by_merchant=False)

        # Generate email
        email_html = templates.generate_weekly_email(product_offers=product_offers)
        if out_dir:
            out_path = out_dir / f"{request.to_addr[:5]}.html"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(email_html)
            _logger.info(f"Email saved to {out_path}")

        # Send email
        if not dry_run:
            providers.MailerSend.send(
                email_html=email_html, to_addrs=[request.to_addr], from_addr=os.environ["FROM_ADDRESS"]
            )
            _logger.info(f"Email sent to {censor_email_addr(request.to_addr)}")
