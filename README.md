# 🍎 coles_vs_woolies 🍏

[![pass](https://github.com/MattTimms/coles_vs_woolies/actions/workflows/test.yml/badge.svg)](https://github.com/MattTimms/coles_vs_woolies/actions/workflows/test.yml)
[![working just fine for me](https://github.com/MattTimms/coles_vs_woolies/actions/workflows/run.yml/badge.svg)](https://github.com/MattTimms/coles_vs_woolies/actions/workflows/run.yml)

Receive an email every week comparing the price of products you buy often.  
I like Connoisseur Ice Cream, but I'll be damned if I'm paying full price for it.

## Demo

## Motivation

I've caught myself checking the grocery catalogues for half-price choccy & ice-cream each week. So, naturally, I've
sought to automate the process & have the price comparison across Aussie grocers, Woolies & Coles, emailed to me
instead.

I looked at existing
platforms, [DiscountKit](https://discountkit.com.au/) & [PriceHipster](https://pricehipster.com/woolworths-hostile), but
they allege that Woolies, in particular, have deliberately blocked their access. Not in the business' best interest, I
suppose. Regardless, if your website is public then it can be scrapped.

## Requirements

This project is first-and-foremost for me. I do have plans for public use but, for the time being, you'll need the

* A [MailerSend](https://www.mailersend.com/) account & it's API key
* A domain verified with MailerSend ([link](https://www.mailersend.com/help/how-to-verify-and-authenticate-a-sending-domain))

[MailerSend](https://www.mailersend.com/) is an email & notifications SaaS with a free-tier that suits personal use.
You'll need to own a domain & verify it with the platform, such that emails can be sent from
that domain i.e `from: no-reply@mydomain.com`.  
This project also leverages MailSenders' email template features so consider that if you wish to incorporate your own
email provider.

## Usage

```shell
pip install -r requirements.txt
```

```shell
~$ python coles_vs_woolies send \
  "Cadbury Dairy Milk Chocolate Block 180g" \
  "Connoisseur Ice Cream Vanilla Caramel Brownie 4 Pack" \
  --to_addr <me@gmail.com> <you@gmail.com> \
  --from_addr <no-reply@domain.com> \
  --mailersend_api_key=<MAILERSEND_API_KEY>

#> Emails sent: 1
#>
#>  shopping list                              coles   woolies
#> ────────────────────────────────────────────────────────────
#>  Cadbury Dairy Milk Chocolate Block 180g    $3.85      $5.5
#>  Cadbury Dairy Milk Vanilla Sticks 4 Pack    $6.5      $9.5
```

```shell
$ python coles_vs_woolies --help
# usage: coles_vs_woolies [-h] {display,send} ...
# 
# Compare prices between Aussie grocers
# 
# positional arguments:
#   {display,send}
#     display       Display product price comparisons
#     send          Email product price comparisons
# 
# options:
#   -h, --help      show this help message and exit
# 
# example:
#     python coles_vs_woolies send
#         "Cadbury Dairy Milk Chocolate Block 180g"
#         "Connoisseur Ice Cream Vanilla Caramel Brownie 4 Pack"
#         --to_addr <me@gmail.com>
#         --to_addr <you@gmail.com>
#         --from_addr <no-reply@domain.com>
#         --mailersend_api_key=<MAILERSEND_API_KEY>
```

## Install w/ GitHub Actions




## What can't it do well?

The out-of-the-box solution takes an optimistic approach to product-search - equivalent to Google's "I'm feeling lucky".
Consequently, there are some edge-cases that are listed below, and I advise for the inclusion of the product's brand,
weight, and/or package size in the search-term provided.

The email will display the search-term used rather than the referenced grocer's product, which may vary due. You can
always find out which product the price belongs to by clicking the price which will direct you to the product's webpage.
Alternatively, the `display` command will show verbose details to help tailor search-terms for weekly emails.

### Product Exclusives

If you searched for a product exclusive to one of the grocers, the other grocer may suggest an equivalent. E.g. "
Unfortunately, we couldn't find results for 'Coles Kitchen Coleslaw 200g' but here's 'Woolworths Classic Coleslaw
200g'". The suggestion system between merchants is quite good, to be honest, so you may not find this an issue.

### Wacky stuff (non-food products)

Thanks, Aldi, for encouraging other grocery chains to start selling desk-chairs & circular-saws - it helps make for a
lot of edge cases that I don't want to bother with. I mean, who's checking each week for the merchant with the
cheapest fog-machines. Note, less wacky non-food products should be fine; e.g. batteries, sanitary products, etc.

## Future plans

I have plans for a site where you can search & add specific items to be compared & emailed weekly. This will
significantly drop the barrier-to-entry & my non-coder friends will be much happier. It also requires that I brush up my
React.js skills, so this will take time.

If you like my work, the best way you can support is:
<p><a href="https://www.buymeacoffee.com/matthewtimms"> <img align="left" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="35" width="147" alt="matthewtimms" /></a></p><br><br>