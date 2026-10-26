import re
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, create_project, delete_project, modal, main_content, goto,
                                    expect_toast, unique_tag, PROJECTS_URL)


def test_search_project():
    """Search for a project and delete it from the search results. The test creates its own project,
    so it never deletes real data and does not depend on an 'Automation' project existing."""
    name = f"QA Delete Project {unique_tag()}"
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            create_project(page, name)
            goto(page, f"{PROJECTS_URL}?search={quote(name)}")
            # page-level locator: filter(has=...) looks for it inside the card
            title = page.locator("h3 a").filter(has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))
            expect(title).to_have_count(1)

            card = main_content(page).locator("div.rounded-2xl").filter(has=title).last
            card.locator("button.border-red-300").click()
            modal(page, "Are you sure you want to delete the project").get_by_role("button", name="Delete").click()
            expect_toast(page, "Project deleted successfully.")

            goto(page, f"{PROJECTS_URL}?search={quote(name)}")
            expect(title).to_have_count(0)
        finally:
            delete_project(page, name)
            browser.close()
