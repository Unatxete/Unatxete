#!/usr/bin/env python3
"""Regenerate the profile sidebar SVGs (dark and light) with the PUBLIC follower count.

Fetches the follower count for the repository owner and hands it to sidebar_card.build(),
which lays the card out again so the followers line stays accurate.
No private-repository data is ever requested or written.

Requires only the Python standard library. Reads:
  GH_TOKEN  - a read-only token (see .github/workflows/profile-stats.yml)
  GH_LOGIN  - the GitHub login to report on (defaults to Unatxete)
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

import sidebar_card

HERE = os.path.dirname(os.path.abspath(__file__))
API_URL = "https://api.github.com/graphql"

QUERY = """
query($login:String!){
  user(login:$login){
    followers{ totalCount }
  }
}
"""


def graphql(query: str, variables: dict, token: str, login: str) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode()
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
    return body["data"]["user"]


def fetch_followers(login: str, token: str) -> int:
    user = graphql(QUERY, {"login": login}, token, login)
    return user["followers"]["totalCount"]


def main() -> int:
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN is not set")
    login = os.environ.get("GH_LOGIN", "Unatxete")

    followers = fetch_followers(login, token)
    for theme in sidebar_card.THEMES:
        with open(os.path.join(HERE, f"{theme}_sidebar.svg"), "w", encoding="utf-8") as fh:
            fh.write(sidebar_card.build(theme, followers))
    print("sidebar SVGs updated: followers =", followers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
