from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_analytics, analytics_table, kpi_value


def test_manual_review_table():
    """OA-003: Manual Review Required lists documents with name, type, confidence and extraction method."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_analytics(page)
        table = analytics_table(page, "Manual Review Required")

        expect(table.get_by_role("columnheader")).to_have_text(["Name", "Document", "Confidence", "Method"])
        rows = table.locator("tbody tr")
        expect(rows.first).to_be_visible()
        assert rows.count() <= int(kpi_value(page, "Manual Review"))
        for row in rows.all():
            cells = [c.strip() for c in row.locator("td").all_inner_texts()]
            assert len(cells) == 4 and cells[0] and cells[1], cells
            assert cells[3] in {"vision", "ocr_ai", "ocr"}, cells

        browser.close()
