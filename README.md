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
  taken from the page's links). Next to it `paths.json`: the same paths for the chatbot's
  categories only, which the page script reads to repair product links the bot mistypes.
- **Schedule:** `.github/workflows/catalog.yml` runs `snapshot.py catalog` every 15 minutes
  (GitHub may start it a few minutes late) and on demand (Actions → catalog → Run workflow).
  A failed read publishes nothing, so the last good file stays.
- **Product details:** `https://raw.githubusercontent.com/yagizozcanrise/aygaz-katalog/details/<product id>.json`
  (`details` branch): each in-scope product page's `props.pageProps.detail` (specs, compatible
  tubes, campaigns, description, accessories, …); only the chatbot's main categories
  (barbecues 159 and 784, heaters 160, camping 161) are read. Read every 2 hours by
  `.github/workflows/details.yml`, 4 pages at a time. A run starts from the last published
  files, reads the products without a file and then the oldest, stops starting pages after
  15 minutes and publishes what it has. A run with more than 20% failed pages publishes
  nothing.
- **Freshness:** the tool falls back to reading the site live when the catalog or a
  product's details are older than 6 hours, missing or broken. Price and stock in a
  product's details are replaced with the catalog's.
- **Suggested questions:** `questions.json` on `main`
  (`https://raw.githubusercontent.com/yagizozcanrise/aygaz-katalog/main/questions.json`), edited
  by hand, not by the snapshot. The chat's opening suggestion buttons on a product page and the
  tool's `get` (`suggested_questions`) both read it. See "Suggested questions".

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

### On a schedule from a Mac

`schedule.sh` runs `publish.sh` every 4 hours with launchd, from a clone in
`~/Library/Application Support/aygaz-katalog` (macOS keeps background jobs out of
`~/Desktop`), pulling `main` before each run:

```bash
./schedule.sh install     # runs now, then every 4 hours
./schedule.sh status      # last runs (log: ~/Library/Logs/aygaz-katalog.log)
./schedule.sh uninstall
```

It runs only while the Mac is awake and logged in; a run missed during sleep starts on
wake. When no run has published for 6 hours, the tool reads the site live as before.
The scheduled job uses the copy of `publish.sh` on GitHub, so push changes before they
take effect.

## Suggested questions

`questions.json` holds the questions Aygaz wants offered for a product, by product id, by
subcategory id (`CategoryID`) or by main category id (`MainCategoryID`):

```json
{
  "products": {"1002": ["Chelsea 420 G kaç kişilik?"]},
  "categories": {"394": ["Kaç kg taşır?", "Katlanınca ölçüleri ne?"]},
  "main_categories": {"160": ["Isı gücü ne kadar?"]}
}
```

The most specific level that has questions for the product is used (product, then
subcategory, then main category); the levels are not mixed. On the product page the chat shows
those first and fills the rest of its 4 buttons with its automatic ones ("Bu ürün hangi tüple
çalışır?" only when the product has compatible tubes, "Öne çıkan özellikleri neler?", …), so a
level can set 1-4 questions. Ids are in the product page path (`…-kid-<main>/…-kid-<sub>/…-pid-<id>`)
and in `catalog.json`. Write questions the product page can answer (its specs, features,
compatible tubes, accessories); a question the page has no answer to sends the visitor to the
call centre. Push to `main`; GitHub serves the change within 5 minutes.

Only public data from the site's own pages is stored here.
