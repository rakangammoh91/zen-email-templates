"""Klaviyo REST API client for the Zen Hair marketing agent.

Thin wrapper with retries, rate-limit backoff, and the revision header.
Matches the auth pattern used by existing scripts in this repo.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

REVISION = "2024-10-15"


class KlaviyoClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("KLAVIYO_PRIVATE_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "KLAVIYO_PRIVATE_API_KEY not set. "
                "Put it in .env locally or in GitHub Actions secrets."
            )
        self.headers = {
            "Authorization": f"Klaviyo-API-Key {self.api_key}",
            "accept": "application/vnd.api+json",
            "content-type": "application/vnd.api+json",
            "revision": REVISION,
        }
        self.base = "https://a.klaviyo.com/api"

    # ---- core HTTP ----
    def _request(self, method: str, path: str, body: dict | None = None, retries: int = 5) -> dict:
        url = f"{self.base}{path}" if path.startswith("/") else path
        data = json.dumps(body).encode() if body else None
        last_err: Exception | None = None
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
                with urllib.request.urlopen(req, timeout=60) as resp:
                    raw = resp.read()
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                last_err = e
                if e.code == 429:
                    wait = 10 * (attempt + 1)
                    print(f"  [429] backoff {wait}s (attempt {attempt + 1}/{retries})", file=sys.stderr)
                    time.sleep(wait)
                    continue
                if e.code >= 500:
                    wait = 5 * (attempt + 1)
                    print(f"  [{e.code}] server error, retry in {wait}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                # 4xx other than 429 → surface with body
                try:
                    err_body = e.read().decode()
                except Exception:
                    err_body = "(no body)"
                raise RuntimeError(f"Klaviyo {method} {path} → {e.code}: {err_body}") from e
            except urllib.error.URLError as e:
                last_err = e
                wait = 5 * (attempt + 1)
                time.sleep(wait)
        raise RuntimeError(f"Klaviyo {method} {path} failed after {retries} retries: {last_err}")

    def get(self, path: str, params: dict | None = None) -> dict:
        if params:
            path = f"{path}?{urllib.parse.urlencode(params)}"
        return self._request("GET", path)

    def post(self, path: str, body: dict) -> dict:
        return self._request("POST", path, body=body)

    # ---- domain helpers ----
    def flow_values_report(
        self,
        flow_ids: list[str],
        statistics: list[str],
        timeframe_key: str,
        conversion_metric_id: str,
    ) -> dict:
        """Pull aggregated flow performance.

        timeframe_key: one of 'last_1_days', 'last_7_days', 'last_30_days',
                       'last_90_days', 'last_365_days', 'this_week', etc.
        """
        body = {
            "data": {
                "type": "flow-values-report",
                "attributes": {
                    "statistics": statistics,
                    "timeframe": {"key": timeframe_key},
                    "conversion_metric_id": conversion_metric_id,
                    "filter": "and("
                    + ",".join(f"equals(flow_id,\"{fid}\")" for fid in flow_ids[:1])
                    + ")" if len(flow_ids) == 1
                    else f"any(flow_id,[{','.join(chr(34)+fid+chr(34) for fid in flow_ids)}])",
                },
            }
        }
        return self.post("/flow-values-reports/", body)

    def get_flow(self, flow_id: str) -> dict:
        return self.get(f"/flows/{flow_id}/")
