import datetime
import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, main_content, ui_date, today

CLOCK = re.compile(r"([A-Za-z ]+) \(GMT([+-])(\d{2}):(\d{2})\)\s*(\d{1,2}):(\d{2})\s*(AM|PM)")


def test_world_clock():
    """DB-003: the clock card shows two time zones whose times match the real time in that zone
    (within two minutes), and today's date."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        main = main_content(page)
        card = main.locator("div.grid.grid-cols-2").filter(has=page.locator("svg circle")).first
        expect(card).to_be_visible()

        clocks = CLOCK.findall(card.inner_text())
        assert len(clocks) == 2, f"expected two clocks, got {clocks} from {card.inner_text()!r}"
        now = datetime.datetime.now(datetime.timezone.utc)
        for zone, sign, hh, mm, hour, minute, ampm in clocks:
            offset = datetime.timedelta(hours=int(hh), minutes=int(mm)) * (1 if sign == "+" else -1)
            expected = now + offset
            shown_hour = int(hour) % 12 + (12 if ampm == "PM" else 0)
            shown = expected.replace(hour=shown_hour, minute=int(minute), second=0, microsecond=0)
            # shown and expected can straddle midnight, so compare minutes on a 24h circle
            diff = abs((shown - expected.replace(second=0, microsecond=0)).total_seconds()) % 86400
            assert min(diff, 86400 - diff) <= 120, f"{zone.strip()}: shows {hour}:{minute} {ampm}, expected ~{expected:%I:%M %p}"

        expect(main.get_by_text(ui_date(today()), exact=True)).to_be_visible()
        browser.close()
