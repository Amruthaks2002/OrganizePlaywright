import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_user_progress, main_content, roadmap_steps, COMPLETED_USER_ID


def test_quiz_performance():
    """UP-003: Quiz Performance expands to show the step's quiz result (status, pass mark, score)
    and collapses again."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_user_progress(page, COMPLETED_USER_ID)
        main = main_content(page)

        roadmap_steps(page).first.click()
        expect(main.get_by_text("onboarding 1 — Quiz")).to_be_visible()
        assert re.search(r"onboarding 1 — Quiz\s+PASSED\s+Passing Criteria\s+70%\s+Quiz Score\s+83\.33%",
                         main.inner_text(), re.I), main.inner_text()
        expect(main.get_by_role("link", name="View Quiz Result").or_(
            main.get_by_role("button", name="View Quiz Result"))).to_be_visible()

        roadmap_steps(page).first.click()
        expect(main.get_by_text("Passing Criteria")).to_have_count(0)

        browser.close()
