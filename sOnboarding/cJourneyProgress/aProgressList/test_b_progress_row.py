from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_progress, progress_url, progress_row, user_progress_url, COMPLETED_USER, COMPLETED_USER_ID,
)


def test_progress_row():
    """JP-002: a row shows the employee, email, journey, % and steps completed, status and the progress link."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page, progress_url(search=COMPLETED_USER))

        row = progress_row(page, COMPLETED_USER)
        expect(row).to_have_count(1)
        for text in ["anjana@iocod.com", "Employe onboarding", "100%", "2 / 2 steps completed"]:
            expect(row).to_contain_text(text)
        expect(row).to_contain_text("Completed", ignore_case=True)
        expect(row.get_by_role("link", name="View Journey Progress")).to_have_attribute(
            "href", user_progress_url(COMPLETED_USER_ID))

        browser.close()
