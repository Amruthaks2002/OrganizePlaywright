import time
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_clone_template():
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

        # a KRA/KPI created without designations is Global, so it can be
        # attached to a template for any designation
        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(500)
        kra_modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Create New KRA").first
        kra_modal.locator("input[placeholder='e.g., Technical Skills']").fill("QA Clone Template Category " + _SUFFIX)
        kra_modal.get_by_role("button", name="Create KRA").click()
        expect(page.get_by_text("Category created successfully.")).to_be_visible(timeout=10000)

        search_kra = main.locator("input[placeholder*='Search KRAs']")
        search_kra.fill("QA Clone Template Category " + _SUFFIX)
        page.wait_for_timeout(1000)
        kra_text = main.get_by_text("QA Clone Template Category " + _SUFFIX, exact=True).first
        kra_text.locator("xpath=ancestor::*[6]").locator("button[title='Add KPI']").click()
        page.wait_for_timeout(500)
        kpi_modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Create New KPI").first
        kpi_modal.locator("input[placeholder='e.g., Code Quality']").fill("QA Clone Template Criterion " + _SUFFIX)
        kpi_modal.get_by_role("button", name="Create KPI").click()
        expect(page.get_by_text("Criterion created successfully.")).to_be_visible(timeout=10000)

        page.get_by_test_id("sidebar-child-review-templates").click()
        page.wait_for_timeout(1500)

        # create a template to clone
        main.get_by_role("button", name="New Template").click()
        page.wait_for_timeout(500)
        desig_input = main.locator("input[placeholder='Select designation']")
        desig_input.click()
        page.wait_for_timeout(500)
        listbox = page.locator("[id^=vs][id$=__listbox]").first
        listbox.get_by_role("option", name="Software Tester", exact=True).click()
        main.locator("input[placeholder*='Performance Appraisal Form']").fill("QA Test Template P " + _SUFFIX)
        main.get_by_role("button", name="Next Step").click()
        page.wait_for_timeout(1000)

        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(500)
        kra_combo = main.locator("input[type=search]").last
        kra_combo.click()
        page.wait_for_timeout(500)
        kra_listbox = page.locator("[id^=vs][id$=__listbox]").last
        kra_listbox.get_by_role("option", name="QA Clone Template Category " + _SUFFIX, exact=True).click()
        main.locator("input[type=number]").fill("100")
        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(1000)

        main.get_by_role("button", name="Add KPI").click()
        page.wait_for_timeout(500)
        kpi_combo = main.locator("input[type=search]").last
        kpi_combo.click()
        page.wait_for_timeout(500)
        kpi_listbox = page.locator("[id^=vs][id$=__listbox]").last
        kpi_listbox.get_by_role("option", name="QA Clone Template Criterion " + _SUFFIX, exact=True).click()
        main.locator("input[type=number]").last.fill("1")
        main.get_by_role("button", name="Add KPI").click()
        page.wait_for_timeout(1000)

        main.get_by_role("button", name="Next Step").click()
        page.wait_for_timeout(1000)
        main.get_by_role("button", name="Save Template").click()
        expect(page.get_by_text("Template created successfully.")).to_be_visible(timeout=10000)

        # clone it
        search = main.locator("input[placeholder='Search templates...']")
        search.fill("QA Test Template P " + _SUFFIX)
        page.wait_for_timeout(2500)
        row = main.locator(".hidden.lg\\:block div.grid").filter(has_text="QA Test Template P " + _SUFFIX)
        row.locator("button").nth(2).click()
        page.wait_for_timeout(500)
        page.get_by_role("button", name="Clone", exact=True).click()
        page.wait_for_timeout(800)
        clone_modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Clone Review Template").first
        clone_modal.get_by_role("button", name="Clone Template").click()
        expect(page.get_by_text("cloned successfully", exact=False)).to_be_visible(timeout=10000)

        search.fill("")
        page.wait_for_timeout(500)
        search.fill("QA Test Template P " + _SUFFIX)
        page.wait_for_timeout(2500)
        rows = main.locator(".hidden.lg\\:block div.grid").filter(has_text="QA Test Template P " + _SUFFIX)
        expect(rows).to_have_count(2)

        # cleanup both the original and the clone
        for _ in range(2):
            rows = main.locator(".hidden.lg\\:block div.grid").filter(has_text="QA Test Template P " + _SUFFIX)
            rows.first.locator("button").nth(2).click()
            page.wait_for_timeout(500)
            page.get_by_role("button", name="Delete", exact=True).click()
            page.wait_for_timeout(500)
            confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Confirm Delete").first
            confirm.get_by_role("button", name="Delete").click()
            expect(page.get_by_text("Template deleted", exact=False)).to_be_visible(timeout=10000)
            page.wait_for_timeout(1000)
            search.fill("QA Test Template P " + _SUFFIX)
            page.wait_for_timeout(2500)

        # a KRA must be deactivated before it or its KPI can be deleted
        page.get_by_test_id("sidebar-child-template-content").click()
        page.wait_for_timeout(1500)
        search_kra.fill("QA Clone Template Category " + _SUFFIX)
        page.wait_for_timeout(1000)
        kra_row = main.get_by_text("QA Clone Template Category " + _SUFFIX, exact=True).first.locator("xpath=ancestor::*[6]")
        kra_row.locator("button").first.click()  # expand the row
        page.wait_for_timeout(1000)
        kra_row.locator("button").nth(2).click(force=True)
        page.wait_for_timeout(1500)
        kra_row.locator("button[title='Delete KPI']").click()
        page.wait_for_timeout(600)
        confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Are you sure").first
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Criterion deleted successfully.")).to_be_visible(timeout=10000)

        kra_row.locator("button[title='Delete KRA']").click()
        page.wait_for_timeout(600)
        confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Are you sure").first
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Category deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
