# aygaz-katalog

A snapshot of the www.aygaz.com.tr product catalog, refreshed every 15 minutes, for the
Aygaz chatbot's `aygaz_products` tool. The site's `/urunler` page takes 5-10 s to serve;
this file is read in a fraction of a second.

- **File:** `https://raw.githubusercontent.com/yagizozcanrise/aygaz-katalog/data/catalog.json`
  (`data` branch, one commit, replaced on every run; GitHub caches it for up to 5 minutes).
- **Content:** `read_at` (Istanbul time), `products` (the page's `__NEXT_DATA__`
  `props.pageProps.products`, unchanged) and `paths` (product id → working page path,
  taken from the page's links).
- **Schedule:** `.github/workflows/catalog.yml` runs `snapshot.py` every 15 minutes
  (GitHub may start it a few minutes late) and on demand (Actions → catalog → Run workflow).
  A failed read publishes nothing, so the last good file stays.
- **Freshness:** the tool falls back to reading the site live when the file is older than
  an hour, missing or broken. Product pages (`get`) are always read live.

Only public data from the site's own pages is stored here.
