# CHANGELOG.md

## v1.3.0

* Added support for merchant-exclusive products
* Added Jaccard similarity sorting for better accuracy results
* Dropped Python3.9 support
* Refactored CLI entry
* Fixed missing merchant in email
* Fixed IGA no-results if query >50 chars
* Fixed email formatting for no-offer-merchants

## v1.2.0

* Added `iga` merchant 
* Added CLI import shopping list from txt file
* Added CLI import of multiple shopping lists from json file

## v1.1.0 - 26/01/2023

* Added `bcc` when sending to multiple recipients
* Added _on-sale_ distinction in price comparisons
* Added additional improvements to display/CLI examples
* Fixed incorrect usage examples
* Fixed cron schedule to suit local time

## v1.0.0 - 24/01/2023

* Initial release 🙌
* Support for `woolies`, `coles`, `mailersend`