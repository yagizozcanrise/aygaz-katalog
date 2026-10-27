#!/bin/sh
# Read the catalog (and, unless "catalog" is given, every product page) from this machine
# and publish them to the data and details branches, as the workflows would.
set -eu
cd "$(dirname "$0")"
what="${1:-all}"
repo="https://yagizozcanrise@github.com/yagizozcanrise/aygaz-katalog.git"
helper='!f() { test "$1" = get && echo username=yagizozcanrise && echo password=$(gh auth token --user yagizozcanrise); }; f'
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

publish() {  # publish <dir> <branch> <message>
    (cd "$1" && git init -q -b "$2" && git add . \
        && git -c user.name="catalog bot" -c user.email="actions@users.noreply.github.com" commit -q -m "$3" \
        && git -c credential.helper= -c credential.helper="$helper" push -q --force "$repo" "$2")
}

stamp="$(date -u +%Y-%m-%dT%H:%MZ)"
mkdir "$work/data"
python3 snapshot.py catalog "$work/data/catalog.json"
publish "$work/data" data "Catalog snapshot $stamp (by hand)"

if [ "$what" != "catalog" ]; then
    DETAILS_BUDGET_S=1500 python3 snapshot.py details "$work/details"
    publish "$work/details" details "Product details $stamp (by hand)"
fi
echo "published $what at $stamp"
