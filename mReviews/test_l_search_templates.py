from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_search_templates():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-reviews").click()
        page.get_by_test_id("sidebar-child-review-templates").click()
        main = page.get_by_test_id("main-content")

        search = main.locator("input[placeholder='Search templates...']")
        search.fill("PMM Template 2026")
        page.wait_for_timeout(2500)  # the search list is debounced
        matches = main.locator(".hidden.lg\\:block div.grid").filter(has_text="PMM Template 2026")
        expect(matches).to_have_count(1)

        search.fill("a template name that matches nothing at all xyz123")
        page.wait_for_timeout(2500)
        expect(main.locator(".hidden.lg\\:block div.grid").filter(has_text="PMM Template 2026")).to_have_count(0)

        browser.close()
