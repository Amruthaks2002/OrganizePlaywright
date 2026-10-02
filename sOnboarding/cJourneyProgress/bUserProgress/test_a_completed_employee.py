import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_progress, progress_url, progress_row, main_content, user_progress_url, COMPLETED_USER,
    COMPLETED_USER_ID,
)


def test_completed_employee():
    """UP-001: View Journey Progress for an employee who finished shows their details, 100%,
    the Onboarding Completed banner and every step completed with its date."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page, progress_url(search=COMPLETED_USER))
        progress_row(page, COMPLETED_USER).get_by_role("link", name="View Journey Progress").click()
        expect(page).to_have_url(user_progress_url(COMPLETED_USER_ID))
        main = main_content(page)

        expect(main.get_by_role("heading", name="Onboarding Progress")).to_be_visible()
        text = main.inner_text()
        for expected in [r"NAME\s+Anjana Anil", r"EMAIL\s+anjana@iocod\.com", r"COMPLETED ON\s+17 Jun, 2026, 09:24 AM",
                         r"ASSIGNED JOURNEY\s+Employe onboarding", r"100%\s+2 / 2 Steps Completed",
                         r"Onboarding Completed\s+This employee has successfully completed all onboarding steps",
                         r"STEP 1\s+REQUIRED\s+onboarding 1\s+Completed on 16 Jun, 2026, 06:07 PM\s+COMPLETED",
                         r"STEP 2\s+REQUIRED\s+onb2\s+Completed on 17 Jun, 2026, 09:24 AM\s+COMPLETED"]:
            assert re.search(expected, text, re.I), f"missing {expected!r}"
        expect(main.get_by_text("Current Step")).to_have_count(0)

        browser.close()
