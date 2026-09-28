import re
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_preview_template():
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
        row = main.locator(".hidden.lg\\:block div.grid").filter(has_text="PMM Template 2026")
        row.get_by_role("button", name="Preview", exact=True).click()
        page.wait_for_timeout(1000)

        expect(page).to_have_url(re.compile(r"/reviews/templates/\d+$"))
        expect(main).to_contain_text("PMM Template 2026")
        expect(main).to_contain_text("Product Marketing Manager")
        expect(main).to_contain_text("Template Structure")
        expect(main).to_contain_text("Total Template Weight")

        main.get_by_role("link", name="Back to List").click()
        page.wait_for_timeout(1000)
        expect(page).to_have_url("https://organice.qc.iocod.com/reviews/templates")

        browser.close()
