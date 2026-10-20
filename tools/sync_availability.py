#!/usr/bin/env python3
"""Pull Beds24 iCal feeds and write assets/data/availability.json.

Each bungalow style is one Beds24 room with 2 units. Its iCal export is set to
"Unavailable Dates", so the feed only lists nights when every unit of that
style is booked or blocked, with no guest details - the same information the
website shows. That is why the feed URLs can live in the repository.

    python3 tools/sync_availability.py
"""
import datetime as dt
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "data", "availability.json")
HORIZON_DAYS = 400
FEED = "https://api.beds24.com/ical/bookings.ics?roomid={}"
ROOMS = {"mangosteen": 744783, "pomelo": 744782, "tamarind": 744781}
UNITS_PER_STYLE = 2


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "dalisay-availability-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse_date(value):
    """Return a date from an iCal DTSTART/DTEND value (DATE or DATE-TIME)."""
    m = re.match(r"(\d{4})(\d{2})(\d{2})", value)
    return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def booked_nights(ics):
    """Set of nights (dates) covered by the feed's events. DTEND is exclusive."""
    text = re.sub(r"\r?\n[ \t]", "", ics)  # unfold continued lines
    nights = set()
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", text, re.S):
        start = re.search(r"^DTSTART[^:\n]*:(\S+)", block, re.M)
        end = re.search(r"^DTEND[^:\n]*:(\S+)", block, re.M)
        if not start:
            continue
        s = parse_date(start.group(1))
        e = parse_date(end.group(1)) if end else s + dt.timedelta(days=1)
        if e <= s:
            e = s + dt.timedelta(days=1)
        d = s
        while d < e:
            nights.add(d)
            d += dt.timedelta(days=1)
    return nights


def to_ranges(dates):
    """[[first_night, checkout_day], ...] - checkout day exclusive, like iCal."""
    out = []
    for d in sorted(dates):
        if out and out[-1][1] == d:
            out[-1][1] = d + dt.timedelta(days=1)
        else:
            out.append([d, d + dt.timedelta(days=1)])
    return [[a.isoformat(), b.isoformat()] for a, b in out]


def main():
    today = dt.date.today()
    horizon = today + dt.timedelta(days=HORIZON_DAYS)

    styles = {}
    for style, room_id in ROOMS.items():
        full = {d for d in booked_nights(fetch(FEED.format(room_id))) if today <= d < horizon}
        styles[style] = {"units": UNITS_PER_STYLE, "booked": to_ranges(full)}

    data = {"updated": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            "styles": styles}

    # Only rewrite the file when the booked dates change, so the scheduled job
    # doesn't commit a new version every run just for the timestamp.
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding="utf-8"))
        if old.get("styles") == styles:
            print("No change in availability")
            return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
        f.write("\n")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
