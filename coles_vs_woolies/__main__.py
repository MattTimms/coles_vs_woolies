import logging
import pathlib

from coles_vs_woolies import search, send_weekly_email
from coles_vs_woolies.utils import session


def _search(keyword: str, **kwargs):
    search_result = search.Search(keyword=keyword)
    search_result.display()


def cli():
    import argparse

    parser = argparse.ArgumentParser(prog=__package__, description="Compare prices between Aussie grocers")
    subparsers = parser.add_subparsers(title="actions")
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("-v", "--verbose", action="store_true")

    search_parser = subparsers.add_parser("search", parents=[parent_parser], help="Search products")
    search_parser.add_argument("keyword", nargs="+", type=str, help="Product name to search")
    search_parser.set_defaults(func=_search)

    email_parser = subparsers.add_parser("email", parents=[parent_parser], help="Emails search results")
    email_parser.add_argument(
        "filepath", type=pathlib.Path, help="Path to a JSON config shopping list; see `shopping-list.example.json`"
    )
    email_parser.add_argument("-o", "--out_dir", type=pathlib.Path, help="Directory to save copy of email HTML")
    email_parser.add_argument("-d", "--dry_run", action="store_true", help="Disable email delivery")
    email_parser.set_defaults(func=send_weekly_email)

    cache_parser = subparsers.add_parser("cache", help="Clears requests' cache")
    cache_parser.set_defaults(func=session.clear_cache)

    args = parser.parse_args()
    if args.verbose:
        logger = logging.getLogger(__package__)
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
    if args.func == _search and isinstance(args.keyword, list):
        args.keyword = " ".join(args.keyword)

    args = vars(args)
    func = args.pop("func")
    func(**args)


if __name__ == "__main__":
    cli()
