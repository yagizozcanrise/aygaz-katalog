"""
Snapshot of the www.aygaz.com.tr product catalog for the Aygaz chatbot's tool.

The /urunler page embeds the whole catalog in its __NEXT_DATA__ JSON but takes 5-10 s
to serve. This script reads it once and writes catalog.json:

    {"read_at": "2026-10-26T14:30:00+03:00",
     "products": [...],               # props.pageProps.products, as the site sends them
     "paths": {"1002": "/urunler/..."}}  # each product's working page path from the page's links

The tool (aygaz_products) reads this file instead of the page and falls back to the
page when the file is missing, stale or broken. Standard library only.
"""

from datetime import datetime, timedelta, timezone
import gzip
import json
import re
import sys
import urllib.request

URL = "https://www.aygaz.com.tr/urunler"
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
ISTANBUL = timezone(timedelta(hours=3))


def read_page() -> str:
    request = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=90) as response:
        body = response.read()
        if response.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
    return body.decode("utf-8")


def snapshot(page: str) -> dict:
    start = page.find(NEXT_DATA_OPEN)
    body_start = page.find(">", start) + 1
    end = page.find("</script>", body_start)
    if start < 0 or end < 0:
        raise ValueError("no __NEXT_DATA__ on the page (the site's structure may have changed)")
    products = json.loads(page[body_start:end])["props"]["pageProps"]["products"]
    if len(products) < MIN_PRODUCTS:
        raise ValueError(f"only {len(products)} products on the page")
    paths = {m.group(2): m.group(1) for m in PRODUCT_LINK.finditer(page[:start])}
    return {
        "read_at": datetime.now(ISTANBUL).isoformat(timespec="seconds"),
        "products": products,
        "paths": paths,
    }


def main() -> int:
    out = sys.argv[1] if len(sys.argv) > 1 else "catalog.json"
    try:
        data = snapshot(read_page())
    except Exception as e:  # keep the last good file: the workflow fails and pushes nothing
        print(f"snapshot failed: {e}", file=sys.stderr)
        return 1
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(data['products'])} products, {len(data['paths'])} paths, read_at {data['read_at']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
