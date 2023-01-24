from typing import List, Any, Dict, Tuple

import arrow
from rich import print

from coles_vs_woolies.examples import compare_offers, best_offers_by_merchant, generate_offer_table
from coles_vs_woolies.emailing.generate import generate_weekly_email
from coles_vs_woolies.emailing import mailer_send
from coles_vs_woolies.search import coles, woolies
from coles_vs_woolies.search.types import ProductOffers


def get_product_offers(product_names: List[str]) -> ProductOffers:
    """ Returns ProductOffers object with optimistic search results for product_names. """
    product_offers: Dict[str, List[Any]] = {}
    for name in product_names:
        product_offers[name] = []
        for merchant in [coles, woolies]:
            merchant_product_search = merchant.im_feeling_lucky(name)
            if (product := next(merchant_product_search, None)) is not None:
                product_offers[name].append(product)

        if not product_offers[name]:
            print(f'[yellow]{name} could not be found!')
            product_offers.pop(name)

    if not product_offers:
        raise ValueError('No products could be found')
    return product_offers


def display(products: List[str]):
    """ Displays various product comparisons. """
    product_offers = get_product_offers(products)
    compare_offers(product_offers)
    best_offers_by_merchant(product_offers)
    generate_offer_table(product_offers)


def send(*, products: List[str],
         to_addrs: List[str],
         from_addr: str,
         mailersend_api_key: str = None,
         out_dir: str = None):
    """
    Send email of product comparisons for a given list of products.

    :param products: List of product names to search; providing weight or package size increases success rates.
        e.g. "Cadbury Dairy Milk Chocolate Block 180g" "Connoisseur Ice Cream Vanilla Caramel Brownie 4 Pack".
    :param to_addrs: Recipient's email address.
    :param from_addr: Sender's email address. Domain must match that verified with MailerSend.
    :param mailersend_api_key: MailerSend API key. Must otherwise be accessible from env-vars - see readme.
    :param out_dir: Optional, directory for saving a copy of email HTML template.
    :return:
    """
    product_offers = get_product_offers(products)

    # Prepare file path for saving generated email template
    email_out_filepath = None
    if out_dir:
        time_str = arrow.now().format("YY-MM-DD")
        email_out_filepath = f'{out_dir}/weekly_{time_str}.html'

    # Generate & send email
    email_html = generate_weekly_email(product_offers, out_path=email_out_filepath)
    mailer_send.send(email_html, to_addrs=to_addrs, from_addr=from_addr, mailersend_api_key=mailersend_api_key)

    # Display emailed product comparison
    generate_offer_table(product_offers)


if __name__ == '__main__':
    _common_purchases = [  # Really helps to have weight/quantity
        'Cadbury Dairy Milk Chocolate Block 180g',
        'Cadbury Dairy Milk Vanilla Sticks 4 Pack',
        'Connoisseur Ice Cream Vanilla Caramel Brownie 4 Pack',
        'Connoisseur Ice Cream Vanilla Caramel Brownie 1L',
        'The Juice Brothers 1.5L'
    ]
    display(products=_common_purchases)
