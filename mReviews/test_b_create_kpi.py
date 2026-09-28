import time
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_create_kpi():
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

        # create a KRA to hold the KPI
        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(500)
        kra_modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Create New KRA").first
        kra_modal.locator("input[placeholder='e.g., Technical Skills']").fill("QA Test Category B " + _SUFFIX)
        kra_modal.get_by_role("button", name="Create KRA").click()
        expect(page.get_by_text("Category created successfully.")).to_be_visible(timeout=10000)

        search = main.locator("input[placeholder*='Search KRAs']")
        search.fill("QA Test Category B " + _SUFFIX)
        page.wait_for_timeout(1000)

        text_el = main.get_by_text("QA Test Category B " + _SUFFIX, exact=True).first
        add_kpi_btn = text_el.locator("xpath=ancestor::*[6]").locator("button[title='Add KPI']")
        add_kpi_btn.click()
        page.wait_for_timeout(500)
        kpi_modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Create New KPI").first
        kpi_modal.locator("input[placeholder='e.g., Code Quality']").fill("QA Test Criterion B " + _SUFFIX)
        kpi_modal.get_by_role("button", name="Create KPI").click()

        expect(page.get_by_text("Criterion created successfully.")).to_be_visible(timeout=10000)

        # expand the KRA and verify the KPI is nested under it
        text_el.locator("xpath=ancestor::*[3]").locator("button").first.click()
        page.wait_for_timeout(800)
        row = text_el.locator("xpath=ancestor::*[6]")
        expect(row).to_contain_text("QA Test Criterion B " + _SUFFIX)

        # cleanup: a KRA must be deactivated before its KPI/itself can be deleted
        row.locator("button").nth(2).click(force=True)
        page.wait_for_timeout(1500)
        row.locator("button[title='Delete KPI']").click()
        page.wait_for_timeout(600)
        confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Are you sure").first
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Criterion deleted successfully.")).to_be_visible(timeout=10000)

        row.locator("button[title='Delete KRA']").click()
        page.wait_for_timeout(600)
        confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Are you sure").first
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Category deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
