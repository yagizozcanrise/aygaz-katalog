"""
Snapshots of www.aygaz.com.tr product data for the Aygaz chatbot's tool.

    python snapshot.py catalog OUT.json   # the whole catalog, from the /urunler page
    python snapshot.py details OUT_DIR    # every product's own page, one file per product

The /urunler page embeds the whole catalog in its __NEXT_DATA__ JSON but takes 5-10 s
to serve; each product page takes about 2 s. The tool (aygaz_products) reads these files
instead and falls back to the pages when a file is missing, stale or broken.

catalog: {"read_at": "2026-10-26T14:30:00+03:00",
          "products": [...],                 # props.pageProps.products, as the site sends them
          "paths": {"1002": "/urunler/..."}}   # each product's working page path from the page's links
details: OUT_DIR/<product id>.json =
         {"read_at": ..., "path": "/urunler/...",
          "detail": {...}}                   # props.pageProps.detail, as the site sends it;
                                             # null when the product has no page of its own

Standard library only.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import gzip
import json
import os
import re
import sys
import time
import urllib.request

BASE = "https://www.aygaz.com.tr"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Accept-Encoding": "gzip",
}
# The listing's own links are the reliable product URLs; the WebLink field in the data
# has its two category segments swapped for about half the products.
PRODUCT_LINK = re.compile(r'href="(/urunler/[^"]*-pid-(\d+))"')
NEXT_DATA_OPEN = '<script id="__NEXT_DATA__"'
# The site lists about 410 products; far fewer means a broken page, not a smaller catalog.
MIN_PRODUCTS = 200
# Tubes are out of the chatbot's scope; their pages are not read.
EXCLUDED_MAIN_CATEGORIES = {"Tüpler"}
# A few product pages at a time, so the site isn't loaded more than by a few visitors.
DETAIL_WORKERS = 4
# More failed product pages than this and nothing is published: the site is having trouble.
MAX_DETAIL_FAILURES = 0.2
ISTANBUL = timezone(timedelta(hours=3))


def now() -> str:
    return datetime.now(ISTANBUL).isoformat(timespec="seconds")


def read_page(path: str) -> str:
    request = urllib.request.Request(BASE + path, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=90) as response:
        body = response.read()
        if response.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
    return body.decode("utf-8")


def next_data(page: str) -> tuple:
    """The page's __NEXT_DATA__ JSON and the HTML before it (the rendered markup)."""
    start = page.find(NEXT_DATA_OPEN)
    body_start = page.find(">", start) + 1
    end = page.find("</script>", body_start)
    if start < 0 or end < 0:
        raise ValueError("no __NEXT_DATA__ on the page (the site's structure may have changed)")
    return json.loads(page[body_start:end]), page[:start]


def catalog() -> dict:
    data, markup = next_data(read_page("/urunler"))
    products = data["props"]["pageProps"]["products"]
    if len(products) < MIN_PRODUCTS:
        raise ValueError(f"only {len(products)} products on the page")
    paths = {m.group(2): m.group(1) for m in PRODUCT_LINK.finditer(markup)}
    return {"read_at": now(), "products": products, "paths": paths}


def detail(path: str) -> dict:
    data, _ = next_data(read_page(path))
    return {"read_at": now(), "path": path, "detail": data["props"]["pageProps"].get("detail")}


def write_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def run_catalog(out: str) -> int:
    data = catalog()
    write_json(out, data)
    print(f"{len(data['products'])} products, {len(data['paths'])} paths, read_at {data['read_at']}")
    return 0


def run_details(out_dir: str) -> int:
    cat = catalog()
    wanted = [(str(p["ProductID"]), cat["paths"].get(str(p["ProductID"])))
              for p in cat["products"] if p.get("MainCategoryTitle") not in EXCLUDED_MAIN_CATEGORIES]
    wanted = [(pid, path) for pid, path in wanted if path]
    os.makedirs(out_dir, exist_ok=True)
    began = time.monotonic()

    def one(item):
        pid, path = item
        try:
            write_json(os.path.join(out_dir, pid + ".json"), detail(path))
            return None
        except Exception as e:  # one page failing doesn't stop the others
            return f"{pid}: {e}"

    with ThreadPoolExecutor(DETAIL_WORKERS) as pool:
        failures = [f for f in pool.map(one, wanted) if f]
    print(f"{len(wanted) - len(failures)}/{len(wanted)} product pages in {time.monotonic() - began:.0f} s")
    for f in failures[:10]:
        print("failed", f, file=sys.stderr)
    if len(failures) > MAX_DETAIL_FAILURES * len(wanted):
        print("too many failures: publishing nothing", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ("catalog", "details"):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        return (run_catalog if sys.argv[1] == "catalog" else run_details)(sys.argv[2])
    except Exception as e:  # keep the last good files: the workflow fails and pushes nothing
        print(f"snapshot failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
