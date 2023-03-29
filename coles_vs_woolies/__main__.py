import argparse
import json
import os
import textwrap
from argparse import ArgumentParser
from typing import List

from pydantic import BaseModel

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
    send_parser.add_argument('-t', '--to_addrs', nargs='+', help="Recipients' email address.", required=False)
    send_parser.add_argument('-o', '--out_dir', type=str, help='Directory for saving copy of the email HTML template.',
                             required=False)
    send_parser.add_argument('-d', '--dry_run', action='store_true', help='Disable email delivery',
                             default=False, required=False)

    # Parse inputs
    kwargs = vars(parser.parse_args())
    action = kwargs.pop('action')

    _product_inputs = kwargs.pop('products')
    if os.path.isfile(fp := _product_inputs[0]) and fp.endswith('.json'):
        with open(fp, 'r') as f:
            jobs = [_JsonInput.parse_obj(x) for x in json.load(f)]
        _ = kwargs.pop('to_addrs', None)
        for job in jobs:
            _run(action, job.products, to_addrs=job.to_addrs, **kwargs)
    else:
        if action == 'send' and kwargs.get('to_addrs', None) is None:
            parser.error('the following arguments are required: -t/--to_addrs')
        products = _parse_product_inputs(_product_inputs)
        _run(action, products, **kwargs)


class _JsonInput(BaseModel):
    to_addrs: List[str]
    products: List[str]


def _run(action: str, products: List[str], **kwargs):
    if action == 'send':
        send(products=products, **kwargs)
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
