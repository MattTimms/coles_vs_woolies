""" A collection of display examples for product comparisons """

from collections import defaultdict
from typing import Dict, List

from rich import box
from rich.console import Console
from rich.table import Table

from coles_vs_woolies.search.types import ProductOffers, Merchant, Product

_console = Console()


def compare_offers(product_offers: ProductOffers):
    # Compare all offers by product
    for name in product_offers.keys():
        _console.print('\n' + name, style=None)
        for i, _product in enumerate(sorted(product_offers[name])):
            txt_colour = None if not i else 'grey50'
            _console.print(f'  {_product.merchant.upper()}: {_product}', style=txt_colour)
    _console.print('\n')


def best_offers_by_merchant(product_offers: ProductOffers):
    # Collect the cheapest offer
    cheapest_products_by_merchant: Dict[Merchant, List[Product]] = defaultdict(list)
    for products in product_offers.values():
        cheapest_product = min(products)
        _merchant: Merchant = cheapest_product.merchant
        cheapest_products_by_merchant[_merchant].append(cheapest_product)

    _console.print("[bold yellow]shopping list")
    _console.print(
        {merchant: [str(p) for p in products] for merchant, products in cheapest_products_by_merchant.items()}
    )


def generate_offer_table(product_offers: ProductOffers, verbose: bool = True) -> Table:
    table = Table(show_header=True, header_style="bold yellow", box=box.SIMPLE_HEAD)
    table.add_column("shopping list", max_width=78)
    for merchant in ["coles", "woolies"]:
        table.add_column(merchant, justify="right", max_width=8)

    for product_name, products in product_offers.items():
        lowest_price = min(products).price
        cheapest_product_idx = [i for i in range(len(products)) if products[i].price == lowest_price]
        row = [product_name]
        for i, _product in enumerate(products):
            txt_colour = '[green]' if i in cheapest_product_idx else '[grey85]'
            price = f'${_product.price}' if _product.price is not None else 'n/a'
            row.append(txt_colour + price)
        table.add_row(*row)

    if verbose:
        _console.print(table)

    return table
