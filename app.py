#!/usr/bin/env python3
"""
Fetches the current Bitcoin price (USD) from the public CoinDesk API
and prints it to stdout.

The script exits with status 1 on any error (network failure, unexpected
response format, etc.) so that CI pipelines can detect failures.
"""

import sys
import json
from typing import Any, Dict

import requests


API_URL = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
TIMEOUT = 10  # seconds


def fetch_bitcoin_price() -> float:
    """
    Calls the CoinDesk API and returns the current Bitcoin price in USD.

    Raises:
        RuntimeError: If the request fails or the response format is unexpected.
    """
    try:
        response = requests.get(API_URL, timeout=TIMEOUT)
    except requests.RequestException as exc:
        raise RuntimeError(f"Network error while contacting CoinDesk API: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"CoinDesk API returned unexpected status code {response.status_code}: {response.text}"
        )

    try:
        data: Dict[str, Any] = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse JSON from CoinDesk API: {exc}") from exc

    try:
        price_str = data["bpi"]["USD"]["rate"]
        # The rate comes as a string with commas, e.g. "27,453.1234"
        price = float(price_str.replace(",", ""))
        return price
    except (KeyError, ValueError, TypeError) as exc:
        raise RuntimeError(f"Unexpected data format in CoinDesk response: {exc}") from exc


def main() -> None:
    try:
        price = fetch_bitcoin_price()
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    # Output only the numeric price, easy to consume by downstream steps
    print(price)


if __name__ == "__main__":
    main()