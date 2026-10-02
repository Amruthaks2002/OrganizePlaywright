import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_progress, main_content, vue_select, progress_row, settle


def test_role_filter():
    """JP-006: the role filter lists the roles and shows only employees with the chosen role."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page)
        main = main_content(page)

        vue_select(page, main, "All Roles", "team-lead")
        expect(page).to_have_url(re.compile(r"role=team-lead"))
        settle(page)
        expect(progress_row(page, "Team Lead User")).to_have_count(1)

        main.locator(".v-select").first.locator("input.vs__search").click()
        page.locator("li[role=option]:visible", has_text=re.compile(r"^\s*employee\s*$")).click()
        expect(page).to_have_url(re.compile(r"role=employee"))
        settle(page)
        expect(progress_row(page, "Team Lead User")).to_have_count(0)

        browser.close()
