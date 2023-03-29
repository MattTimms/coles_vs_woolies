import argparse
import os
import textwrap
from argparse import ArgumentParser
from typing import List

from coles_vs_woolies.main import display, send


def cli():
    example_usage = '''example:
    python coles_vs_woolies display
        "Cadbury Dairy Milk Chocolate Block 180g"
        "Connoisseur Ice Cream Vanilla Caramel Brownie 4 Pack"
        
    python coles_vs_woolies send
        "Cadbury Dairy Milk Chocolate Block 180g"
        "Connoisseur Ice Cream Vanilla Caramel Brownie 4 Pack"
        --to_addrs <me@gmail.com> <you@gmail.com> 
        --from_addr <no-reply@domain.com>
        --mailersend_api_key=<MAILERSEND_API_KEY>
    '''

    parser = ArgumentParser(
        prog='coles_vs_woolies',
        description='Compare prices between Aussie grocers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(example_usage)
    )

    subparsers = parser.add_subparsers(dest='action')

    help_product = 'List of descriptive product search terms. Brand, package weight or size should be included. ' \
                   'Can be file path. E.g. "Cadbury Dairy Milk Chocolate Block 180g"' \
                   '"Connoisseur Ice Cream Vanilla Caramel Brownie 4 Pack"'

    # Display parser
    display_parser = subparsers.add_parser('display', help='Display product price comparisons')
    display_parser.add_argument('products', nargs='+', help=help_product)

    # Send parser
    send_parser = subparsers.add_parser('send', help='Email product price comparisons')
    send_parser.add_argument('products', nargs='+', help=help_product)
    send_parser.add_argument('-t', '--to_addrs', nargs='+', help="Recipients' email address.", required=True)
    send_parser.add_argument('-f', '--from_addr', type=str,
                             help="Sender's email address. Domain must match that verified with MailerSend.",
                             required=False)
    send_parser.add_argument('-m', '--mailersend_api_key', type=str, help='MailerSend API key.', required=False)
    send_parser.add_argument('-o', '--out_dir', type=str, help='Directory for saving copy of the email HTML template.',
                             required=False)
    send_parser.add_argument('-d', '--dry_run', type=bool, help='Send to disable email delivery', default=False,
                             required=False)

    args = vars(parser.parse_args())
    products = _parse_product_inputs(args.pop('products'))
    action = args.pop('action')

    if action == 'send':
        send(products=products, **args)
    else:
        display(products=products)


def _parse_product_inputs(args: List[str]) -> List[str]:
    """ Return product list from input list of products/file-paths """
    products = []
    for input_ in args:
        if os.path.isfile(input_):
            with open(input_, 'r') as f:
                products.extend(f.read().splitlines())
        else:
            products.append(input_)
    return sorted(list(set(products)))


if __name__ == '__main__':
    cli()
