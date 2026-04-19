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

# Load .env for local runs. In GitHub Actions, env vars come from secrets directly.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
            # safe='[]' preserves Klaviyo's bracket syntax (additional-fields[segment])
            path = f"{path}?{urllib.parse.urlencode(params, safe='[]')}"
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
        if len(flow_ids) == 1:
            flow_filter = f'equals(flow_id,"{flow_ids[0]}")'
        else:
            quoted = ",".join(f'"{fid}"' for fid in flow_ids)
            flow_filter = f"contains-any(flow_id,[{quoted}])"
        body = {
            "data": {
                "type": "flow-values-report",
                "attributes": {
                    "statistics": statistics,
                    "timeframe": {"key": timeframe_key},
                    "conversion_metric_id": conversion_metric_id,
                    "filter": flow_filter,
                },
            }
        }
        return self.post("/flow-values-reports/", body)

    def get_flow(self, flow_id: str) -> dict:
        return self.get(f"/flows/{flow_id}/")

    # ---- paginated helpers ----
    def paginate(self, path: str, params: dict | None = None, max_pages: int = 50) -> list[dict]:
        """Follow cursor pagination; returns concatenated data[] entries."""
        results: list[dict] = []
        cur_path = path
        cur_params = params.copy() if params else {}
        for _ in range(max_pages):
            page = self.get(cur_path, cur_params if cur_params else None)
            data = page.get("data") or []
            results.extend(data)
            next_link = (page.get("links") or {}).get("next")
            if not next_link:
                break
            # next_link is an absolute URL — strip base and re-request
            cur_path = next_link.replace(self.base, "")
            cur_params = None  # already encoded in next link
        return results

    # ---- campaigns ----
    def list_campaigns(self, channel: str = "email", since_iso: str | None = None) -> list[dict]:
        filt = f'equals(messages.channel,"{channel}")'
        if since_iso:
            filt = f"and({filt},greater-or-equal(scheduled_at,{since_iso}))"
        return self.paginate("/campaigns/", {"filter": filt})

    def campaign_values_report(
        self,
        campaign_ids: list[str],
        statistics: list[str],
        timeframe_key: str,
        conversion_metric_id: str,
    ) -> dict:
        if len(campaign_ids) == 1:
            filt = f'equals(campaign_id,"{campaign_ids[0]}")'
        else:
            quoted = ",".join(f'"{c}"' for c in campaign_ids)
            filt = f"contains-any(campaign_id,[{quoted}])"
        body = {
            "data": {
                "type": "campaign-values-report",
                "attributes": {
                    "statistics": statistics,
                    "timeframe": {"key": timeframe_key},
                    "conversion_metric_id": conversion_metric_id,
                    "filter": filt,
                },
            }
        }
        return self.post("/campaign-values-reports/", body)

    # ---- segments & lists ----
    def list_segments(self) -> list[dict]:
        # profile_count not available as additional-field for segments in this revision;
        # fetch basic inventory, then call /segments/{id}/ individually for counts when needed.
        return self.paginate("/segments/")

    def list_lists(self) -> list[dict]:
        try:
            return self.paginate("/lists/", {"additional-fields[list]": "profile_count"})
        except RuntimeError:
            return self.paginate("/lists/")

    def get_segment_profile_count(self, segment_id: str) -> int | None:
        try:
            resp = self.get(f"/segments/{segment_id}/", {"additional-fields[segment]": "profile_count"})
            return (resp.get("data", {}).get("attributes") or {}).get("profile_count")
        except Exception:
            return None

    # ---- metrics ----
    def list_metrics(self) -> list[dict]:
        return self.paginate("/metrics/")

    def metric_aggregate(
        self,
        metric_id: str,
        measurements: list[str],
        interval: str,
        timezone: str,
        start_iso: str,
        end_iso: str,
    ) -> dict:
        body = {
            "data": {
                "type": "metric-aggregate",
                "attributes": {
                    "metric_id": metric_id,
                    "measurements": measurements,
                    "interval": interval,
                    "timezone": timezone,
                    "filter": [
                        f"greater-or-equal(datetime,{start_iso})",
                        f"less-than(datetime,{end_iso})",
                    ],
                },
            }
        }
        return self.post("/metric-aggregates/", body)

    # ---- flow message (per-email) ----
    def get_flow_messages(self, flow_id: str) -> list[dict]:
        """Flow actions → messages. Used to resolve message IDs to subjects."""
        return self.paginate(f"/flows/{flow_id}/flow-actions/", {"include": "flow-messages"})
