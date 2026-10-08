from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, month_label, month_label_text, next_month, prev_month, day_cell,
                                    today)


def shift(d, months):
    index = d.year * 12 + d.month - 1 + months
    return d.replace(year=index // 12, month=index % 12 + 1, day=1)


def test_month_navigation():
    """DB-026: the next and previous arrows move the calendar a month at a time, label and grid both."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        for months, step in [(1, next_month), (0, prev_month), (-1, prev_month), (-2, prev_month)]:
            step(page)
            target = shift(today(), months)
            expect(month_label(page)).to_have_text(month_label_text(target))
            expect(day_cell(page, target)).not_to_have_class("fc-day-other")
        browser.close()
