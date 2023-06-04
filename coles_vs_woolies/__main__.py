import argparse
import json
from argparse import ArgumentParser

from pydantic import BaseModel, Extra

from coles_vs_woolies.main import send


class ShoppingList(BaseModel, extra=Extra.allow):
    """ Model for the `shopping-list` json config file. """
    to_addrs: list[str]
    products: list[str]


def cli():
    parser = ArgumentParser(
        prog='coles_vs_woolies',
        description='Compare prices between Aussie grocers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('file_path', type=str,
                        help='File path to a JSON config shopping list; see `shopping-list.example.json`')
    parser.add_argument('-o', '--out_dir', type=str, required=False,
                        help='Directory for saving copy of the email HTML template.')
    parser.add_argument('-d', '--dry_run', action='store_true', default=False, required=False,
                        help='Disable email delivery')

    # Parse inputs
    kwargs = vars(parser.parse_args())
    with open(kwargs.pop('file_path'), 'r') as fp:
        shopping_lists: list[ShoppingList] = [ShoppingList.parse_obj(list_) for list_ in json.load(fp)]

    # Run for each shopping list
    for shopping_list in shopping_lists:
        send(products=shopping_list.products,
             to_addrs=shopping_list.to_addrs,
             **kwargs)


if __name__ == '__main__':
    cli()
