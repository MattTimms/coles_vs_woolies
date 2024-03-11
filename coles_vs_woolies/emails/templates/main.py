import pathlib
from datetime import datetime

from ... import merchants

_TEMPLATE_DIR = pathlib.Path(__file__).parent.absolute()


def generate_weekly_email(product_offers: dict[str, list[merchants.ProductClass]]) -> str:
    """Returns an email template populated from product_offers."""
    # Import HTML templates & snippets
    with open(_TEMPLATE_DIR / "weekly.html", "r", encoding="utf-8") as f:
        html_template = f.read()
    with open(_TEMPLATE_DIR / "snippets/table.html", "r", encoding="utf-8") as f:
        html_template_table = f.read()
    with open(_TEMPLATE_DIR / "snippets/table_row.html", "r", encoding="utf-8") as f:
        html_template_table_row = f.read()

    # Sort by "has sale items"
    sorted_product_offers = sorted(
        product_offers.items(), key=lambda items: any(offer.is_on_special for offer in items[-1]), reverse=True
    )

    # Build merchant offer HTML rows from template
    rows = []
    green, light_grey = "#008000", "#afafaf"
    for product_offer in sorted_product_offers:
        product_name, offers = product_offer

        row_template = html_template_table_row
        row_template = row_template.replace("{{ product }}", product_name)

        # Replace merchant offers
        lowest_price = min(offers).price
        is_sales = any(offer.is_on_special for offer in offers)
        merchants_with_offers: set[merchants.MerchantName] = set()
        for offer in offers:
            merchant = offer.merchant
            merchants_with_offers.add(merchant)

            # Determine text replacement details
            price = f"${offer.price}" if offer.price is not None else "-"
            colour = green if is_sales and offer.price == lowest_price else light_grey

            # Insert merchant offer into HTML template
            html_replacement = f'<a href="{offer.url}" style="color:{colour};' f'text-decoration:inherit;">{price}</a>'
            row_template = row_template.replace("{{ %(merchant)s_price }}" % {"merchant": merchant}, html_replacement)

        # Format email for merchants without offers
        for missing_merchant in merchants.merchant_names.difference(merchants_with_offers):
            html_replacement = f'<span style="color:{light_grey};">-</span>'
            row_template = row_template.replace(
                "{{ %(merchant)s_price }}" % {"merchant": missing_merchant}, html_replacement
            )

        rows.append(row_template)

    # Build HTML table of merchant offers
    html_template_table = html_template_table.replace("{{ rows }}", "".join(rows))
    html_template = html_template.replace("{{ table }}", html_template_table)

    # Add timespan to template
    year, week, weekday = datetime.now().isocalendar()
    week_start, week_fin = (week - 1, week) if weekday < 3 else (week, week + 1)
    start, fin = datetime.fromisocalendar(year, week_start, 3), datetime.fromisocalendar(year, week_fin, 2)
    replacement_str = f"Deals from {start.strftime('%a %d/%m')} till {fin.strftime('%a %d/%m')}"
    html_template = html_template.replace("{{ timespan }}", replacement_str)

    return html_template
