# aygaz-katalog

A snapshot of the www.aygaz.com.tr product catalog, refreshed every 15 minutes, and of each
product's page, refreshed every 2 hours, for the Aygaz chatbot's `aygaz_products` tool. The site's `/urunler` page takes 5-10 s to serve;
this file is read in a fraction of a second.

- **File:** `https://raw.githubusercontent.com/yagizozcanrise/aygaz-katalog/data/catalog.json`
  (`data` branch, one commit, replaced on every run; GitHub caches it for up to 5 minutes).
- **Content:** `read_at` (Istanbul time), `products` (the page's `__NEXT_DATA__`
  `props.pageProps.products`, unchanged) and `paths` (product id → working page path,
  taken from the page's links).
- **Schedule:** `.github/workflows/catalog.yml` runs `snapshot.py catalog` every 15 minutes
  (GitHub may start it a few minutes late) and on demand (Actions → catalog → Run workflow).
  A failed read publishes nothing, so the last good file stays.
- **Product details:** `https://raw.githubusercontent.com/yagizozcanrise/aygaz-katalog/details/<product id>.json`
  (`details` branch): each product page's `props.pageProps.detail` (specs, compatible
  tubes, campaigns, description, accessories, …), read every 2 hours by
  `.github/workflows/details.yml`, 4 pages at a time. A run with more than 20% failed pages
  publishes nothing.
- **Freshness:** the tool falls back to reading the site live when the catalog is older
  than an hour or a product's details older than 6 hours, missing or broken. Price and
  stock in a product's details are replaced with the catalog's, which is at most ~20
  minutes old.

Only public data from the site's own pages is stored here.
