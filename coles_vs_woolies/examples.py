""" A collection of display examples for product comparisons """

from collections import defaultdict
from typing import Literal

from rich import box
from rich.console import Console
from rich.table import Table

from coles_vs_woolies.search.similarity import jaccard_similarity
from coles_vs_woolies.search.types import Merchant, Product, ProductOffers

_console = Console()


def compare_offers(product_offers: ProductOffers):
    # Compare all offers by product
    for name, products in product_offers.items():
        _console.print('\n' + name, style='underline')

        lowest_price = min(products).price
        cheapest_product_idx = [i for i in range(len(products)) if products[i].price == lowest_price]
        is_sales = any((_product.is_on_special for _product in products))
        for i, _product in enumerate(products):
            txt_colour = 'green' if is_sales and i in cheapest_product_idx else 'grey50'
            # txt_colour = None if not i else 'grey50'
            similarity = jaccard_similarity(name, _product.display_name)
            _console.print(f'  {_product.merchant.upper()}: {_product} | {similarity=:.2f}', style=txt_colour)
    _console.print('\n')


def best_offers_by_merchant(product_offers: ProductOffers):
    # Collect the cheapest offer
    cheapest_products_by_merchant: dict[Merchant | Literal['either'], list[Product]] = defaultdict(list)
    for products in product_offers.values():
        is_all_same_price = len(set(p.price for p in products)) == 1
        if is_all_same_price:
            cheapest_products_by_merchant['either'].append(products[0])
        else:
            cheapest_product = min(products)
            _merchant: Merchant = cheapest_product.merchant
            cheapest_products_by_merchant[_merchant].append(cheapest_product)

    _console.print("[bold yellow]shopping list")
    _console.print(
        {merchant: [str(p) for p in products] for merchant, products in cheapest_products_by_merchant.items()}
    )


def generate_offer_table(product_offers: ProductOffers, verbose: bool = True) -> Table:
    table = Table(show_header=True, header_style="bold yellow", box=box.SIMPLE_HEAD)
    table.add_column("shopping list", max_width=128)
    for merchant in ["coles", "woolies", "iga"]:
        table.add_column(merchant, justify="right", max_width=8)

    for product_name, products in product_offers.items():
        lowest_price = min(products).price
        cheapest_product_idx = [i for i in range(len(products)) if products[i].price == lowest_price]
        is_sales = any((_product.is_on_special for _product in products))
        row = [product_name]
        for i, _product in enumerate(products):
            txt_colour = '[green]' if is_sales and i in cheapest_product_idx else '[grey85]'
            price = f'${_product.price}' if _product.price is not None else 'n/a'
            row.append(txt_colour + price)
        table.add_row(*row)

    if verbose:
        _console.print(table)

    return table
