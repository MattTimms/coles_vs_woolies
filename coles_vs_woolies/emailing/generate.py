import pathlib
import datetime

from rich.console import Console
from rich.table import Table

from coles_vs_woolies.search.types import ProductOffers

_SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
_TEMPLATE_DIR = _SCRIPT_DIR / 'templates'


def generate_weekly_email(product_offers: ProductOffers, out_path: str = None) -> str:
    """
    Returns a Mailersend email template populated from product_offers & save to out_path.
    :param product_offers: ProductOffers used for populating email template.
    :param out_path: optional, save destination for output email template.
    :return:
    """
    # Import HTML templates & snippets
    with open(_TEMPLATE_DIR / 'weekly.html', 'r', encoding="utf-8") as f:
        html_template = f.read()
    with open(_TEMPLATE_DIR / 'snippets/table.html', 'r', encoding="utf-8") as f:
        html_template_table = f.read()
    with open(_TEMPLATE_DIR / 'snippets/table_row.html', 'r', encoding="utf-8") as f:
        html_template_table_row: str = f.read()

    # Replace template variables
    rows = []
    green = '#008000'
    light_grey = '#afafaf'
    for product_name, offers in product_offers.items():
        row_template = html_template_table_row
        row_template = row_template.replace('{{ product }}', product_name)

        # Replace merchant offers
        lowest_price = min(offers).price
        is_sales = any((offer.is_on_special for offer in offers))
        for offer in offers:
            merchant = offer.merchant
            price = offer.price if offer.price is not None else 'n/a'
            colour = green if is_sales and price == lowest_price else light_grey
            zero_padding = '<span style="opacity:0;">0</span>' if len(str(price).split('.')[-1]) == 1 else ''

            html_replacement =  f'<a href="{offer.link}" style="color:{colour};text-decoration:inherit;">${price}{zero_padding}</a>'
            row_template = row_template.replace('{{ %(merchant)s_price }}' % {"merchant": merchant}, html_replacement)

        rows.append(row_template)

    html_template_table = html_template_table.replace('{{ rows }}', ''.join(rows))
    html_template = html_template.replace('{{ table }}', html_template_table)

    # Add time
    year, week, weekday = datetime.datetime.now().isocalendar()
    week_start, week_fin = (week - 1, week) if weekday < 3 else (week, week + 1)
    start = datetime.datetime.fromisocalendar(year, week_start, 3)
    fin = datetime.datetime.fromisocalendar(year, week_fin, 2)
    html_template = html_template.replace('{{ intro }}',
                                          f"Deals from {start.strftime('%a %d/%m')} till {fin.strftime('%a %d/%m')}")

    # Output formatted template
    if out_path:
        pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding="utf-8") as f:
            f.write(html_template)

    return html_template


def _generate_weekly_template_old(offer_table: Table, out_path: str):
    # TODO this is legacy & requires printing garbage to console
    _console = Console(record=True)
    _console.print(offer_table)
    html_table = _console.export_html(inline_styles=True, code_format="<pre>{code}</pre>")

    with open(_TEMPLATE_DIR / 'old/rich_template.html', 'r') as f:
        html = f.read()

    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding="utf-8") as f:
        f.write(html.replace('{{ table }}', html_table))
