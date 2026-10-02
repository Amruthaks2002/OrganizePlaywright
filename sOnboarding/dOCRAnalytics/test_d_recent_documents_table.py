import datetime
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_analytics, analytics_table


def test_recent_documents_table():
    """OA-004: Recent Documents lists name, type, number, gender and created date, newest first."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_analytics(page)
        table = analytics_table(page, "Recent Documents")

        expect(table.get_by_role("columnheader")).to_have_text(["Name", "Document", "Number", "Gender", "Created"])
        rows = table.locator("tbody tr")
        expect(rows.first).to_be_visible()
        created = []
        for row in rows.all():
            cells = [c.strip() for c in row.locator("td").all_inner_texts()]
            assert len(cells) == 5 and all(cells), cells
            created.append(datetime.datetime.strptime(cells[4], "%d %b, %Y, %I:%M %p"))
        assert created == sorted(created, reverse=True), created

        browser.close()
