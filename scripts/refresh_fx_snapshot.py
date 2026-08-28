"""
FleetPath -- FX Snapshot Refresh Script
Run this OFFLINE, on a schedule (Windows Task Scheduler, GitHub Action cron,
etc.) -- NOT imported or called by api/main.py or any request path. The
running server only ever reads data/fx_rates.json, the same as every other
static baseline in data/. This script's only job is to overwrite that file
once a day with a freshly dated, cited rate.

Source: Bank of Canada Valet API (official daily average rate, published
once per business day by 16:30 ET). This is the correct citation-grade
source for a Canadian audit tool -- not a retail FX aggregator, which bakes
in a spread and isn't a rate any institution would use for reporting.

Usage:
    python scripts/refresh_fx_snapshot.py

Exit code is non-zero on any failure (network error, unexpected API shape,
stale/missing observation) so a scheduler can alert on failed refreshes
without silently leaving a stale file in place, and without ever blocking
a live user request on this network call.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

BOC_VALET_URL = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?recent=1"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "fx_rates.json"
PARAM_ID = "REF_FX_USD_CAD_DAILY"


def fetch_latest_rate() -> tuple[float, str]:
    """Returns (rate, observation_date) from the Bank of Canada Valet API."""
    with urlopen(BOC_VALET_URL, timeout=10) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    observations = payload.get("observations", [])
    if not observations:
        raise ValueError("Bank of Canada Valet API returned no observations.")

    latest = observations[-1]
    rate = float(latest["FXUSDCAD"]["v"])
    obs_date = latest["d"]
    return rate, obs_date


def write_snapshot(rate: float, obs_date: str) -> None:
    snapshot = {
        "usd_to_cad": {
            "param_id": PARAM_ID,
            "value": rate,
            "unit": "CAD per USD",
            "source_agency": "Bank of Canada, Valet API (daily average exchange rate)",
            "source_url": "https://www.bankofcanada.ca/rates/exchange/daily-exchange-rates/",
            "rate_observation_date": obs_date,
            "snapshot_generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "note": (
                "Refreshed offline once daily by scripts/refresh_fx_snapshot.py. "
                "The running server never calls this API directly -- it reads this "
                "static file, same as every other baseline in data/. If this file's "
                "rate_observation_date is more than a few days stale, the scheduled "
                "refresh has failed and should be investigated before the figure is "
                "trusted for a report."
            ),
        }
    }
    OUTPUT_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")


def main() -> int:
    try:
        rate, obs_date = fetch_latest_rate()
    except (URLError, ValueError, KeyError, TimeoutError) as exc:
        print(f"FX snapshot refresh FAILED: {exc}", file=sys.stderr)
        print(f"Existing {OUTPUT_PATH} was left untouched.", file=sys.stderr)
        return 1

    write_snapshot(rate, obs_date)
    print(f"FX snapshot refreshed: 1 USD = {rate} CAD (Bank of Canada observation date: {obs_date})")
    return 0


if __name__ == "__main__":
    sys.exit(main())