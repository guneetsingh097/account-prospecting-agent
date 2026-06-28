#!/usr/bin/env python3
"""
Migraine Weather Alert — Mac mini proactive notifier
====================================================
Run on a schedule (via launchd) to get advance macOS notifications when
a migraine-triggering barometric pressure swing is forecast.

Sends 3 timed alerts per HIGH event:
  • ~48h ahead  → "Plan tonight: sleep, hydrate, stock meds"
  • ~12h ahead  → "Start preventive steps now"
  • Active now  → "HIGH risk active — rescue meds ready"

MEDIUM events get a single 24h-ahead heads-up.

Duplicate notifications are suppressed via a state file so you never get
spammed by the same event across multiple 6-hour checks.

Configuration (set as env vars in the launchd plist):
  MIGRAINE_CITY    city name, e.g. "London"          ← use one of these
  MIGRAINE_LAT     latitude  e.g. "51.5074"
  MIGRAINE_LON     longitude e.g. "-0.1278"
  MIGRAINE_TZ      IANA timezone (optional, default auto)

Usage:
  python3 migraine_alert.py          # normal run
  python3 migraine_alert.py --test   # force a test notification
"""

import os
import json
import sys
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# ── Paths ─────────────────────────────────────────────────────────────────
HOME           = Path.home()
LOG_FILE       = HOME / 'Library/Logs/migraine_tracker.log'
STATE_FILE     = HOME / 'Library/Application Support/MigraineTracker/state.json'
GEOCODE_URL    = 'https://geocoding-api.open-meteo.com/v1/search'
FORECAST_URL   = 'https://api.open-meteo.com/v1/forecast'

# ── Thresholds (hPa change over N hours) ─────────────────────────────────
THRESHOLDS = {
    3:  {'HIGH': 4.0,  'MEDIUM': 2.5},
    24: {'HIGH': 10.0, 'MEDIUM': 6.0},
}
RISK_SCORE = {'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}

# ── Notification windows (hours_until ranges) ─────────────────────────────
# Each event fires at most once per window; dedup key prevents repeat alerts.
NOTIFY_WINDOWS = {
    'HIGH': [
        ('adv',  30, 66,  '📋 Migraine Heads-Up'),   # ~48h ahead
        ('warn',  6, 30,  '⚠️  Migraine Alert'),       # ~12h ahead
        ('now',  -2,  6,  '🚨 Migraine Risk: Active'), # happening now
    ],
    'MEDIUM': [
        ('med',  12, 54,  '💛 Migraine Watch'),        # ~24h ahead
    ],
}

# ── Logging ───────────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-7s  %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
log = logging.getLogger(__name__)


# ── State persistence ─────────────────────────────────────────────────────

def load_state() -> dict:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {'notified': {}}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def prune_old_keys(notified: dict, cutoff_days: int = 7) -> dict:
    """Remove notification keys older than cutoff_days to keep the file tidy."""
    cutoff = datetime.now() - timedelta(days=cutoff_days)
    fresh = {}
    for key in notified:
        # Key format: "2026-06-28T14:00_adv" — extract the date part
        try:
            dt = datetime.fromisoformat(key.split('_')[0])
            if dt >= cutoff:
                fresh[key] = notified[key]
        except Exception:
            pass
    return fresh


# ── macOS notification ─────────────────────────────────────────────────────

def notify(title: str, body: str, sound: str = 'Basso'):
    t = title.replace('"', "'")
    b = body.replace('"', "'")
    script = f'display notification "{b}" with title "{t}" sound name "{sound}"'
    try:
        subprocess.run(['osascript', '-e', script], check=True, timeout=5,
                       capture_output=True)
        log.info(f'  → Notified: {title}')
    except subprocess.CalledProcessError as e:
        log.error(f'osascript error: {e.stderr.decode().strip()}')
    except Exception as e:
        log.error(f'Notification failed: {e}')


# ── Weather data ───────────────────────────────────────────────────────────

def geocode(city: str) -> tuple:
    r = requests.get(GEOCODE_URL,
                     params={'name': city, 'count': 1, 'language': 'en', 'format': 'json'},
                     timeout=10)
    r.raise_for_status()
    results = r.json().get('results', [])
    if not results:
        raise ValueError(f'City not found: "{city}"')
    loc = results[0]
    return (loc['latitude'], loc['longitude'],
            loc.get('timezone', 'auto'), loc['name'], loc.get('country', ''))


def fetch_forecast(lat: float, lon: float, tz: str) -> dict:
    r = requests.get(FORECAST_URL, params={
        'latitude': lat, 'longitude': lon,
        'hourly': 'pressure_msl',
        'forecast_days': 7,
        'timezone': tz,
    }, timeout=15)
    r.raise_for_status()
    return r.json()


# ── Pressure analysis ──────────────────────────────────────────────────────

def compute_risks(pressures: list) -> list:
    n = len(pressures)
    risks = []
    for i in range(n):
        a3  = abs(pressures[min(i + 3,  n - 1)] - pressures[i]) if i + 3  < n else 0
        a24 = abs(pressures[min(i + 24, n - 1)] - pressures[i]) if i + 24 < n else 0
        if a3 >= THRESHOLDS[3]['HIGH'] or a24 >= THRESHOLDS[24]['HIGH']:
            risks.append('HIGH')
        elif a3 >= THRESHOLDS[3]['MEDIUM'] or a24 >= THRESHOLDS[24]['MEDIUM']:
            risks.append('MEDIUM')
        else:
            risks.append('LOW')
    return risks


def find_events(times: list, pressures: list, risks: list) -> list:
    n = len(risks)
    events, i = [], 0
    while i < n:
        if risks[i] in ('HIGH', 'MEDIUM'):
            j, peak = i, risks[i]
            while j < n and risks[j] in ('HIGH', 'MEDIUM'):
                if RISK_SCORE[risks[j]] > RISK_SCORE[peak]:
                    peak = risks[j]
                j += 1
            block = pressures[i:j + 1]
            sp, ep = pressures[i], pressures[min(j, n - 1)]
            events.append({
                'start_time':    times[i],
                'risk_level':    peak,
                'magnitude':     round(max(block) - min(block), 1),
                'direction':     'rising' if ep > sp else 'falling',
                'duration_hours': j - i,
                'start_pressure': round(sp, 1),
                'end_pressure':   round(ep, 1),
            })
            i = j
        else:
            i += 1
    return events


def fmt_when(iso: str) -> str:
    try:
        d = datetime.fromisoformat(iso)
        return d.strftime('%A %b %-d at %-I%p').lower()
    except Exception:
        return iso


# ── Notification message builder ───────────────────────────────────────────

def build_message(ev: dict, window_key: str, hours_until: float, location_name: str) -> tuple[str, str]:
    risk   = ev['risk_level']
    mag    = ev['magnitude']
    dur    = ev['duration_hours']
    dirn   = ev['direction']
    arrow  = '↓' if dirn == 'falling' else '↑'
    when   = fmt_when(ev['start_time'])
    h      = max(0, int(hours_until))

    if risk == 'HIGH':
        if window_key == 'now':
            title = f'🚨 Migraine Risk Active — {location_name}'
            body  = (f"Pressure {arrow} {dirn} {mag} hPa over ~{dur}h. "
                     f"HIGH migraine risk right now. Ensure rescue medication is accessible immediately.")
        elif window_key == 'warn':
            title = f'⚠️  Migraine Alert: HIGH risk in ~{h}h — {location_name}'
            body  = (f"Pressure {arrow} {dirn} {mag} hPa starting {when}. "
                     f"If your son has a preventive protocol, start it now. "
                     f"Minimise triggers: bright light, loud noise, skipped meals.")
        else:  # adv
            title = f'📋 Migraine Heads-Up: HIGH risk in ~{h}h — {location_name}'
            body  = (f"Pressure swing forecast for {when} "
                     f"({arrow} {mag} hPa, ~{dur}h). "
                     f"Plan tonight: prioritise good sleep, extra hydration, and check rescue med supply.")
    else:  # MEDIUM
        title = f'💛 Migraine Watch: MEDIUM risk in ~{h}h — {location_name}'
        body  = (f"Moderate pressure {dirn} ({arrow} {mag} hPa over ~{dur}h) starting {when}. "
                 f"Watch for early signs: aura, light sensitivity, neck tension. Stay hydrated.")

    return title, body


# ── Main ───────────────────────────────────────────────────────────────────

def run(test_mode: bool = False):
    # ── Resolve location ─────────────────────────────────────────
    city    = os.environ.get('MIGRAINE_CITY', '').strip()
    lat_env = os.environ.get('MIGRAINE_LAT', '').strip()
    lon_env = os.environ.get('MIGRAINE_LON', '').strip()
    tz_env  = os.environ.get('MIGRAINE_TZ', 'auto').strip()

    if lat_env and lon_env:
        lat, lon      = float(lat_env), float(lon_env)
        tz            = tz_env
        location_name = city or f'{lat:.3f}, {lon:.3f}'
    elif city:
        lat, lon, tz, name, country = geocode(city)
        location_name = f'{name}, {country}' if country else name
    else:
        log.error('Set MIGRAINE_CITY or MIGRAINE_LAT + MIGRAINE_LON env vars in your launchd plist.')
        sys.exit(1)

    log.info(f'Checking forecast for {location_name} ({lat:.4f}, {lon:.4f}) tz={tz}')

    if test_mode:
        notify('🧠 Migraine Tracker: Test', f'Alert system working for {location_name}. You are set up correctly.', 'Glass')
        log.info('Test notification sent.')
        return

    # ── Fetch + analyse ──────────────────────────────────────────
    weather   = fetch_forecast(lat, lon, tz)
    hourly    = weather.get('hourly', {})
    times     = hourly.get('time', [])
    pressures = hourly.get('pressure_msl', [])

    if not pressures:
        log.error('No pressure data in API response.')
        return

    utc_offset_s = int(weather.get('utc_offset_seconds', 0))
    now_local    = (datetime.now(timezone.utc) + timedelta(seconds=utc_offset_s)).replace(tzinfo=None)

    risks  = compute_risks(pressures)
    events = find_events(times, pressures, risks)

    # ── Load dedup state ─────────────────────────────────────────
    state    = load_state()
    notified = state.get('notified', {})
    sent     = 0

    # ── Check each event against notification windows ─────────────
    for ev in events:
        try:
            ev_start    = datetime.fromisoformat(ev['start_time'])
            hours_until = (ev_start - now_local).total_seconds() / 3600
        except Exception:
            continue

        risk = ev['risk_level']
        for win_key, lo, hi, _ in NOTIFY_WINDOWS.get(risk, []):
            if lo <= hours_until < hi:
                dedup_key = f"{ev['start_time']}_{win_key}"
                if dedup_key in notified:
                    log.info(f'  Skip (already sent): {dedup_key}')
                    continue

                title, body = build_message(ev, win_key, hours_until, location_name)
                notify(title, body)
                notified[dedup_key] = datetime.now().isoformat()
                sent += 1

    # ── Save pruned state ─────────────────────────────────────────
    state['notified'] = prune_old_keys(notified)
    state['last_run'] = now_local.isoformat()
    state['location'] = location_name
    save_state(state)

    log.info(f'Done. {len(events)} events in 7-day forecast, {sent} notification(s) sent.')


if __name__ == '__main__':
    test = '--test' in sys.argv
    try:
        run(test_mode=test)
    except Exception as e:
        log.error(f'Alert script failed: {e}', exc_info=True)
        sys.exit(1)
