# 🍎 coles_vs_woolies 🍏

![Python](https://img.shields.io/badge/python-3.11-blue)
[![pass](https://github.com/MattTimms/coles_vs_woolies/actions/workflows/test.yml/badge.svg)](https://github.com/MattTimms/coles_vs_woolies/actions/workflows/test.yml)
[![working just fine for me](https://github.com/MattTimms/coles_vs_woolies/actions/workflows/run.yml/badge.svg)](https://github.com/MattTimms/coles_vs_woolies/actions/workflows/run.yml)

🍅 `iga` now supported. (not that their online store is any good)

Receive an email every week comparing the price of products you buy often.

Scrap Aussie grocers' public APIs, schedule a GitHub Action to run weekly, and
leverage [MailerSend](https://www.mailersend.com/)'s free-tier as an email service provider.

I am working on a user-friendly website ([read more](#future-plans)). However, in the meantime, you can read below &
set up your own weekly email service, or simply play with it as CLI tool.

## Demo

<p align="center">
  <img src="/.github/imgs/demo.gif" width="100%" height="100%" />
</p>

## Motivation

> _"I like Connoisseur ice cream, but I'll be damned if I'm paying full price for it."_


I have caught myself checking the grocery catalogues for half-price choccy & ice-cream each week. So, naturally, I've
sought to automate the process & have the cheapest offer across Aussie grocers, Woolies & Coles, emailed to me
instead.

I looked at existing
platforms, [DiscountKit](https://discountkit.com.au/) & [PriceHipster](https://pricehipster.com/woolworths-hostile),
however they allege that Woolies, in particular, have deliberately blocked their services. Regardless, supporting the
developer community is a good thing & if your website is public then it can/will be scrapped.

## Requirements

* A [MailerSend](https://www.mailersend.com/) account & it's API key
* A domain verified with
  MailerSend ([help](https://www.mailersend.com/help/how-to-verify-and-authenticate-a-sending-domain))

[MailerSend](https://www.mailersend.com/) is an email & notifications SaaS with a free-tier that suits personal use.
You'll need to own a domain & verify it with the platform, such that emails can be sent from
that domain i.e `from: no-reply@mydomain.com`.
This project also leverages MailSenders' email template features so consider that if you wish to incorporate your own
email provider.

## Usage

```shell
pip install .
```

```shell
$ python coles_vs_woolies --help
usage: coles_vs_woolies [-h] {search,email,cache} ...

Compare prices between Aussie grocers

options:
  -h, --help            show this help message and exit

actions:
  {search,email,cache}
    search              Search products
    email               Emails search results
    cache               Clears requests' cache
```

```shell
cp .env.example .env
# populate .env to simplify calls
cp shopping-list.example.json shopping-list.json
# populate the shopping list with your email & desired items
```

## Install w/ GitHub Actions

n.b. I found sporadic success with GitHub-hosted runners; I would recommend setting
up [self-hosted GitHub runners](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners)
for consistent success if you wished to continue using GitHub actions rather than running a simple cron job.

1. Fork this repo
2. Read the GitHub Action workflow [run.yml](.github/workflows/run.yml)
3. Add GitHub Action Variables & Secrets for those in the [run.yml](.github/workflows/run.yml)
    - n.b. storing a `shopping-list.json` as a minified json string should do the job
4. Manually invoke the GitHub Action & confirm an email was received

## Getting the best results

An optimistic approach to product-search is used - equivalent to Google's "I'm feeling lucky". Consequently, there are
some edge-cases and I advise for the inclusion of the product's brand, weight, and/or package size in the search-term
provided.

The email will display the search-term used rather than the individual grocer's search-result product. This can vary. If
a search-term is too vague, the first-item returned may not be what you're looking for. You can always find out which
product the price belongs to by clicking the price which will direct you to the product's webpage.
Alternatively, the `display` command will show verbose details to help tailor search-terms for weekly emails.

```
❌ "Chocolate" - too generic
❌ "Cadbury Chocolate" - still too generic
✔️ "Cadbury Chocolate 180g" - now we're talking!
✔️ "Cadbury Dairy Milk Chocolate Block 180g" - yes!
```

### Brand Family

If it wasn't clear by now, I'm a fan of Cadbury chocolate and I have learnt that, generally, the entire product family
goes on sale at the same time; that is to say most chocolate flavours go on sale: "Dairy Milk", "Marvellous
Creations", "Caramilk", etc. You can avoid adding every individual product by picking the one that best represents the
product family.

### Product Exclusives

If you searched for a product that is exclusive to one of the grocers, the other grocer may suggest an equivalent.
E.g. "Unfortunately, we couldn't find results for 'Coles Kitchen Coleslaw 200g' but here's 'Woolworths Classic Coleslaw
200g'". The suggestion system between merchants is quite good, to be honest, so you may not find this an issue.

### Wacky stuff (non-food products)

Thanks, Aldi, for encouraging other grocery chains to start selling desk-chairs & circular-saws - it helps make for a
lot of edge cases that I don't want to bother with. I mean, who's checking each week for the merchant with the
cheapest fog-machines? Note, less wacky non-food products should be fine; e.g. batteries, sanitary products, etc.

## Future plans

I have begun building a site where you can search & add specific items as a personalised weekly subscription. This will
significantly drop the barrier-to-entry & my non-coder friends will be much happier. It also requires that I brush up my
React.js skills, so this will take time.

If you like my work or wish to support this project going forward, the best way you can is to
<p><a href="https://www.buymeacoffee.com/matthewtimms"> <img align="left" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="35" width="147" alt="matthewtimms" /></a></p><br><br>
