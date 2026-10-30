#!/usr/bin/env python3
"""Read-only LAN dashboard for the latest Raspberry Pi health report."""

from __future__ import annotations

import argparse
from datetime import datetime
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import ipaddress
from pathlib import Path
import re


PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_NAME = re.compile(r"health-\d{4}-\d{2}-\d{2}_\d{6}\.md\Z")
FIELD = re.compile(r"^- ([A-Za-z ]+):\s*(.*?)\s*$")
ALLOWED_STATUS = {"OK", "WARNING", "CRITICAL", "UNKNOWN"}


def latest_report(reports_dir: Path) -> dict[str, str] | None:
    """Read a single newest report and return only explicitly allowed fields."""
    candidates = [
        path for path in reports_dir.iterdir()
        if REPORT_NAME.fullmatch(path.name) and path.is_file() and not path.is_symlink()
    ] if reports_dir.is_dir() else []
    if not candidates:
        return None

    report = max(candidates, key=lambda path: path.name)
    if report.stat().st_size > 64 * 1024:
        return None
    parsed: dict[str, str] = {}
    for line in report.read_text(encoding="utf-8", errors="replace").splitlines():
        match = FIELD.fullmatch(line)
        if match:
            parsed[match.group(1)] = match.group(2)

    result: dict[str, str] = {}
    hostname = parsed.get("Hostname", "")
    if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", hostname):
        result["Hostname"] = hostname

    date = parsed.get("Date", "")
    try:
        datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        result["Date"] = date
    except ValueError:
        pass

    patterns = {
        "CPU Load": (r"\d+(?:\.\d+)?", "CPU Load"),
        "RAM Usage": (r"\d{1,3}% \[(?:OK|WARNING|CRITICAL)\]", "RAM Usage"),
        "Disk Usage": (r"\d{1,3}% \[(?:OK|WARNING|CRITICAL)\]", "Disk Usage"),
        "CPU Temperature": (r"(?:\d{1,3}(?:\.\d+)?|N/A) C \[(?:OK|WARNING|CRITICAL|UNKNOWN)\]", "CPU Temperature"),
        "Failed Services": (r"\d{1,6} \[(?:OK|WARNING|CRITICAL)\]", "Failed Services"),
    }
    for field, (pattern, key) in patterns.items():
        value = parsed.get(field, "")
        if re.fullmatch(pattern, value):
            result[key] = value

    uptime = parsed.get("Uptime", "")
    if re.fullmatch(r"[A-Za-z0-9 ,:.()-]{1,80}", uptime):
        result["Uptime"] = uptime

    overall = parsed.get("Overall Status", "")
    if overall in ALLOWED_STATUS:
        result["Overall Status"] = overall
    return result


def render_dashboard(data: dict[str, str] | None) -> bytes:
    if data and data.get("Overall Status") in ALLOWED_STATUS:
        status = data["Overall Status"]
        status_class = status.lower()
        rows = [
            ("CPU load", data.get("CPU Load", "Unavailable")),
            ("Memory", data.get("RAM Usage", "Unavailable")),
            ("Disk", data.get("Disk Usage", "Unavailable")),
            ("CPU temperature", data.get("CPU Temperature", "Unavailable")),
            ("Failed services", data.get("Failed Services", "Unavailable")),
            ("Uptime", data.get("Uptime", "Unavailable")),
        ]
        metrics = "\n".join(
            f'<div class="metric"><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>'
            for label, value in rows
        )
        heading = f"Health: {escape(status)}"
        details = escape(data.get("Hostname", "Raspberry Pi"))
        timestamp = escape(data.get("Date", "Date unavailable"))
    else:
        status_class = "unknown"
        heading = "No health report yet"
        details = "Run scripts/health-check.sh on the Raspberry Pi to create one."
        timestamp = ""
        metrics = '<div class="empty">The dashboard only reads reports in this project’s reports/ folder.</div>'

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="60"><title>Raspberry Pi Health</title>
<style>
:root{{color-scheme:light dark;font:16px system-ui,sans-serif}}body{{margin:0;background:#101820;color:#eef4f7}}
main{{max-width:760px;margin:7vh auto;padding:24px}}header,.card{{background:#192833;border:1px solid #344956;border-radius:16px;padding:24px;margin-bottom:18px}}
h1{{margin:0 0 8px;font-size:1.5rem}}.muted{{color:#b4c3cc;margin:0}}.badge{{display:inline-block;padding:8px 14px;border-radius:999px;font-weight:700;margin:20px 0 12px}}
.ok{{background:#14532d;color:#dcfce7}}.warning{{background:#854d0e;color:#fef3c7}}.critical{{background:#7f1d1d;color:#fee2e2}}.unknown{{background:#334155;color:#f1f5f9}}
dl{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:0}}.metric{{background:#223642;border-radius:12px;padding:16px}}
dt{{color:#b4c3cc;font-size:.9rem}}dd{{margin:8px 0 0;font-size:1.2rem;font-weight:650;overflow-wrap:anywhere}}footer{{color:#b4c3cc;font-size:.9rem;margin:20px 4px}}
</style></head><body><main><header><h1>Raspberry Pi Health</h1><p class="muted">Latest local monitoring report · refreshes every minute</p>
<div class="badge {status_class}">{heading}</div><p class="muted">{details}</p></header>
<section class="card"><dl>{metrics}</dl></section>
<footer>Report time: {timestamp} · This page reads selected metrics only.</footer></main></body></html>"""
    return page.encode("utf-8")


class DashboardHandler(BaseHTTPRequestHandler):
    reports_dir: Path

    def do_GET(self) -> None:
        if self.path != "/":
            self.send_error(404)
            return
        try:
            body = render_dashboard(latest_report(self.reports_dir))
        except (OSError, UnicodeError):
            body = render_dashboard(None)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        # Avoid writing client addresses or request details to logs.
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve a read-only local health dashboard.")
    parser.add_argument("--host", default="127.0.0.1", help="IPv4 address of this Pi; defaults to localhost")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--reports", type=Path, default=PROJECT_DIR / "reports")
    args = parser.parse_args()

    try:
        address = ipaddress.ip_address(args.host)
        if (
            address.version != 4
            or address.is_unspecified
            or address.is_reserved
            or address.is_multicast
            or not (address.is_loopback or address.is_private or address.is_link_local)
        ):
            raise ValueError
    except ValueError:
        parser.error("--host must be a specific local IPv4 address (loopback, private, or link-local), not a public or all-interface address")
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    DashboardHandler.reports_dir = args.reports.expanduser().resolve()
    server = HTTPServer((str(address), args.port), DashboardHandler)
    print(f"Dashboard listening at http://{address}:{args.port}/ (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
