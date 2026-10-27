# aygaz-katalog

Snapshots of www.aygaz.com.tr product data for the Aygaz chatbot's `aygaz_products` tool:
the catalog and each product's page. For now both are refreshed by hand with `publish.sh`
(see "Refreshing by hand").
The site takes 5-10 s to serve the catalog page and about 2 s per product page; these
files are read in a fraction of a second.

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
  `.github/workflows/details.yml`, 4 pages at a time. A run starts from the last published
  files, reads the products without a file and then the oldest, stops starting pages after
  15 minutes and publishes what it has. A run with more than 20% failed pages publishes
  nothing.
- **Freshness:** the tool falls back to reading the site live when the catalog or a
  product's details are older than 6 hours, missing or broken. Price and stock in a
  product's details are replaced with the catalog's.

## Refreshing by hand

GitHub's scheduler starts the catalog workflow only a few times a day, and the site times
out product pages for GitHub's runners (the details workflow is disabled). Until this runs
elsewhere on a schedule, refresh both from a machine in Turkey at least every 6 hours:

```bash
./publish.sh            # catalog and all product pages (about 3 minutes)
./publish.sh catalog    # catalog only (about 10 seconds)
```

It needs `python3`, `git` and the GitHub CLI logged in as `yagizozcanrise`. It reads the
pages with `snapshot.py` and replaces the `data` and `details` branches. A failed read
publishes nothing.

Only public data from the site's own pages is stored here.
