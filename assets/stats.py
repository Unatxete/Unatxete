#!/usr/bin/env python3
"""Regenerate the profile card SVGs (dark and light) with PUBLIC-only GitHub aggregates.

Fetches four unambiguously public figures for the repository owner and writes them
into the committed terminal-panel SVGs by replacing the text of elements addressed by
`id`. No private-repository data (names, line counts, private activity) is ever
requested or written: every field below is derived from PUBLIC repositories only.

Requires only the Python standard library. Reads:
  GH_TOKEN  - a read-only token (see .github/workflows/profile-stats.yml)
  GH_LOGIN  - the GitHub login to report on (defaults to UnaxAlonso0)
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_PATHS = [os.path.join(HERE, f"{theme}_mode.svg") for theme in ("dark", "light")]
API_URL = "https://api.github.com/graphql"

QUERY = """
query($login:String!){
  user(login:$login){
    followers{ totalCount }
    repositories(privacy:PUBLIC, ownerAffiliations:OWNER){ totalCount }
    repositoriesContributedTo(privacy:PUBLIC, contributionTypes:[COMMIT,PULL_REQUEST,ISSUE,REPOSITORY]){ totalCount }
    ownedStars: repositories(privacy:PUBLIC, ownerAffiliations:OWNER, first:100){ nodes{ stargazerCount } }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    payload = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"{login}-profile-stats",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.load(resp)
    if "errors" in body:
        raise SystemExit(f"GraphQL errors: {body['errors']}")
    user = body["data"]["user"]
    return {
        "v_repos": user["repositories"]["totalCount"],
        "v_stars": sum(n["stargazerCount"] for n in user["ownedStars"]["nodes"]),
        "v_followers": user["followers"]["totalCount"],
        "v_contrib": user["repositoriesContributedTo"]["totalCount"],
    }


def apply(svg: str, values: dict) -> str:
    for element_id, value in values.items():
        # Replace the text content of <tspan ... id="element_id">OLD</tspan> in place.
        pattern = re.compile(
            r'(<tspan\b[^>]*\bid="' + re.escape(element_id) + r'"[^>]*>)[^<]*(</tspan>)'
        )
        new_svg, count = pattern.subn(rf"\g<1>{value}\g<2>", svg)
        if count != 1:
            raise SystemExit(f"expected exactly one element id={element_id!r}, found {count}")
        svg = new_svg
    return svg


def main() -> int:
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN is not set")
    login = os.environ.get("GH_LOGIN", "UnaxAlonso0")

    values = fetch(login, token)
    for path in SVG_PATHS:
        with open(path, encoding="utf-8") as fh:
            svg = fh.read()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(apply(svg, values))
    print("card SVGs updated:", values)
    return 0


if __name__ == "__main__":
    sys.exit(main())
