import time
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_search_kra():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        login(page)
        _SUFFIX = str(int(time.time() * 1000))[-6:]
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-reviews").click()
        page.get_by_test_id("sidebar-child-template-content").click()
        main = page.get_by_test_id("main-content")

        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(500)
        modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Create New KRA").first
        modal.locator("input[placeholder='e.g., Technical Skills']").fill("QA Test Category C " + _SUFFIX)
        modal.get_by_role("button", name="Create KRA").click()
        expect(page.get_by_text("Category created successfully.")).to_be_visible(timeout=10000)

        search = main.locator("input[placeholder*='Search KRAs']")
        search.fill("QA Test Category C " + _SUFFIX)
        page.wait_for_timeout(1000)
        cards = main.locator("h4")
        expect(cards).to_have_count(1)
        expect(cards.first).to_contain_text("QA Test Category C " + _SUFFIX)

        search.fill("a search term that matches nothing at all xyz123")
        page.wait_for_timeout(1000)
        expect(main.get_by_text("QA Test Category C " + _SUFFIX, exact=True)).to_have_count(0)

        # cleanup: a KRA must be deactivated before it can be deleted
        search.fill("QA Test Category C " + _SUFFIX)
        page.wait_for_timeout(1000)
        kra_row = main.get_by_text("QA Test Category C " + _SUFFIX, exact=True).first.locator("xpath=ancestor::*[6]")
        kra_row.locator("button").nth(2).click(force=True)
        page.wait_for_timeout(1500)
        kra_row.locator("button[title='Delete KRA']").click()
        page.wait_for_timeout(600)
        confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Are you sure").first
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Category deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
