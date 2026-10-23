import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_user_progress, main_content, roadmap_steps, IN_PROGRESS_USER_ID


def test_quiz_not_attended():
    """UP-004: a quiz the employee hasn't taken shows NOT ATTENDED and no score.

    Known bug: the score shows as "N/A%". This test fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_user_progress(page, IN_PROGRESS_USER_ID)
        main = main_content(page)

        roadmap_steps(page).first.click()
        expect(main.get_by_text("NOT ATTENDED", exact=False)).to_be_visible()
        expect(main.get_by_text("Passing Criteria")).to_be_visible()
        assert not re.search(r"N/A\s*%", main.inner_text()), "the missing score is shown as \"N/A%\""

        browser.close()
