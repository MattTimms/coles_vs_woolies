from rich import box
from rich.console import Console
from rich.table import Table

from ..merchants import ProductClass

_console = Console()


def product_table(title: str, products: list[ProductClass], caption: str | None = None):
    if not products:
        _console.print(f"No results... ({title} | {caption})", style="italic")
        return

    is_single_merchant = len(set(product.merchant for product in products)) == 1

    table = Table(title=title, caption=caption, box=box.SIMPLE_HEAD, show_header=True, header_style="bold magenta")
    if not is_single_merchant:
        table.add_column("Merchant")
    table.add_column("Index")
    table.add_column("Product")
    table.add_column("Price", justify="right")
    table.add_column("Size", justify="right")
    table.add_column("Price per Unit", justify="right")
    table.add_column("Sale")
    table.add_column("Url")

    lowest_price = min(products).price
    for product in products:
        is_lowest_price = product.price == lowest_price

        # Styles
        style_price = "" if not is_lowest_price else "[green]" if product.is_on_special else "[yellow]"
        style_text = "[green]" if is_lowest_price and product.is_on_special else ""

        data = [
            str(product.index),
            style_text + product.display_name,
            style_price + f"${float(product.price):.2f}" if product.price else "-",
            product.size,
            (product.price_per_unit or "-"),
            product.label or "discounted" if product.is_on_special else "",
            str(product.url),
        ]
        if not is_single_merchant:
            data.insert(0, style_text + product.merchant)
        table.add_row(*data)

    _console.print(table)
