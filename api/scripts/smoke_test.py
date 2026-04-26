"""
End-to-end smoke test for the API.

Run with the server running on localhost:8000:
    python -m api.scripts.smoke_test

Exits non-zero on any failure. Use this as a pre-deploy sanity check.
"""

import json
import sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError


BASE = "http://localhost:8000"


def check(label: str, ok: bool, detail: str = ""):
    marker = "✓" if ok else "✗"
    print(f"  {marker} {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        sys.exit(1)


def post_form(path: str, form: dict) -> dict:
    data = urlencode(form).encode()
    req = Request(BASE + path, data=data, method="POST",
                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(req) as resp:
        return json.loads(resp.read())


def get_json(path: str, token: str | None = None) -> dict | list:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(BASE + path, headers=headers)
    with urlopen(req) as resp:
        return json.loads(resp.read())


def main():
    print("\nSmoke test — Safety Operations API")
    print("=" * 40)

    # Health
    h = get_json("/health")
    check("GET /health", h.get("status") == "ok")

    # Login
    tok = post_form("/auth/login", {"username": "admin", "password": "admin123"})
    token = tok.get("access_token")
    check("POST /auth/login", bool(token), f"user={tok['user']['username']}")

    # Me
    me = get_json("/auth/me", token)
    check("GET /auth/me", me.get("username") == "admin")

    # Dashboard endpoints
    kpis = get_json("/dashboard/kpis?year=2022", token)
    check("GET /dashboard/kpis", kpis.get("total_incidents", 0) > 0,
          f"total={kpis.get('total_incidents'):,}")

    trend = get_json("/dashboard/trend?months=24", token)
    check("GET /dashboard/trend", len(trend) > 0, f"{len(trend)} points")

    states = get_json("/dashboard/states?year=2022&top_n=5", token)
    check("GET /dashboard/states", len(states) == 5,
          f"top={states[0]['state']}")

    weather = get_json("/dashboard/weather?year=2022", token)
    check("GET /dashboard/weather", len(weather) > 0, f"{len(weather)} rows")

    hotspots = get_json("/dashboard/hotspots?year=2022&top_n=10", token)
    check("GET /dashboard/hotspots", len(hotspots) == 10,
          f"top={hotspots[0]['city']}")

    years = get_json("/dashboard/years", token)
    check("GET /dashboard/years", len(years.get("years", [])) > 0,
          f"{years['years']}")

    # Auth should reject bad creds
    try:
        post_form("/auth/login", {"username": "admin", "password": "WRONG"})
        check("reject bad password", False, "did not raise")
    except HTTPError as e:
        check("reject bad password", e.code == 401, "got 401 as expected")

    print("=" * 40)
    print("All green ✓\n")


if __name__ == "__main__":
    main()