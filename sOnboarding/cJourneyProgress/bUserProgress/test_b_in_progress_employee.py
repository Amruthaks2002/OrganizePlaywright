import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_user_progress, main_content, IN_PROGRESS_USER, IN_PROGRESS_USER_ID


def test_in_progress_employee():
    """UP-002: an employee who hasn't finished shows 0%, In Progress, the current step,
    and the remaining steps as pending."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_user_progress(page, IN_PROGRESS_USER_ID)
        main = main_content(page)

        text = main.inner_text()
        for expected in [rf"NAME\s+{IN_PROGRESS_USER}", r"0%\s+0 / 2 Steps Completed\s+In Progress",
                         r"Current Step\s+Step 1\s+onboarding 1",
                         r"STEP 1\s+REQUIRED\s+onboarding 1\s+CURRENT", r"STEP 2\s+REQUIRED\s+onb2\s+PENDING"]:
            assert re.search(expected, text, re.I), f"missing {expected!r}"
        expect(main.get_by_text("COMPLETED ON")).to_have_count(0)
        expect(main.get_by_text("Onboarding Completed")).to_have_count(0)

        browser.close()
