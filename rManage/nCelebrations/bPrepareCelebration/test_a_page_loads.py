from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_prepare, main_content, EMPLOYEE, CELEBRATION_DATE_TEXT,
)


def test_page_loads():
    """PC-001: Prepare Celebration shows the employee, date, years and all three steps completed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_prepare(page)
        main = main_content(page)

        expect(main.get_by_text(EMPLOYEE, exact=True).first).to_be_visible()
        expect(main.get_by_text(CELEBRATION_DATE_TEXT, exact=True).first).to_be_visible()
        expect(main.get_by_text("(2 years)", exact=True)).to_be_visible()
        for step, hint in [("User Image", "Used for all celebrations"), ("Template", "Background"),
                           ("Final Image", "Generate/Upload")]:
            expect(main.get_by_text(step, exact=True).first).to_be_visible()
            expect(main.get_by_text(hint, exact=True).first).to_be_visible()
        # the progress bar is the first block holding all three step hints
        progress = main.get_by_text("Generate/Upload", exact=True).locator(
            "xpath=ancestor::div[contains(., 'Used for all celebrations') and contains(., 'Background')][1]")
        expect(progress.get_by_text("✓", exact=True)).to_have_count(3)
        for heading in ["Step 1: User Image", "Step 2: Select Template", "Step 3: Final Image",
                        "Final Image Preview", "Custom Message", "Celebration Details"]:
            expect(main.get_by_role("heading", name=heading)).to_be_visible()

        browser.close()
