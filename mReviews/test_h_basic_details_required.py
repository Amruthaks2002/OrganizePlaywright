import time
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_basic_details_required():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        login(page)
        _SUFFIX = str(int(time.time() * 1000))[-6:]
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-reviews").click()
        page.get_by_test_id("sidebar-child-review-templates").click()
        main = page.get_by_test_id("main-content")

        main.get_by_role("button", name="New Template").click()
        page.wait_for_timeout(500)

        next_btn = main.get_by_role("button", name="Next Step")
        expect(next_btn).to_be_disabled()

        desig_input = main.locator("input[placeholder='Select designation']")
        desig_input.click()
        page.wait_for_timeout(500)
        listbox = page.locator("[id^=vs][id$=__listbox]").first
        listbox.get_by_role("option", name="Software Tester", exact=True).click()

        # designation alone is not enough; the template name is also required
        expect(next_btn).to_be_disabled()

        main.locator("input[placeholder*='Performance Appraisal Form']").fill("QA Test Template H " + _SUFFIX)
        expect(next_btn).to_be_enabled()

        browser.close()
