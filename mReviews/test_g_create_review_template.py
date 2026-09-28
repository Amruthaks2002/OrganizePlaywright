import time
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_create_review_template():
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
        kra_modal.locator("input[placeholder='e.g., Technical Skills']").fill("QA Create Template Category " + _SUFFIX)
        kra_modal.get_by_role("button", name="Create KRA").click()
        expect(page.get_by_text("Category created successfully.")).to_be_visible(timeout=10000)

        search_kra = main.locator("input[placeholder*='Search KRAs']")
        search_kra.fill("QA Create Template Category " + _SUFFIX)
        page.wait_for_timeout(1000)
        kra_text = main.get_by_text("QA Create Template Category " + _SUFFIX, exact=True).first
        kra_text.locator("xpath=ancestor::*[6]").locator("button[title='Add KPI']").click()
        page.wait_for_timeout(500)
        kpi_modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Create New KPI").first
        kpi_modal.locator("input[placeholder='e.g., Code Quality']").fill("QA Create Template Criterion " + _SUFFIX)
        kpi_modal.get_by_role("button", name="Create KPI").click()
        expect(page.get_by_text("Criterion created successfully.")).to_be_visible(timeout=10000)

        page.get_by_test_id("sidebar-child-review-templates").click()
        page.wait_for_timeout(1500)

        main.get_by_role("button", name="New Template").click()
        page.wait_for_timeout(500)  # let the page transition settle

        desig_input = main.locator("input[placeholder='Select designation']")
        desig_input.click()
        page.wait_for_timeout(500)
        listbox = page.locator("[id^=vs][id$=__listbox]").first
        listbox.get_by_role("option", name="Software Tester", exact=True).click()
        main.locator("input[placeholder*='Performance Appraisal Form']").fill("QA Test Template G " + _SUFFIX)
        page.wait_for_timeout(300)
        main.get_by_role("button", name="Next Step").click()
        page.wait_for_timeout(1000)

        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(500)
        kra_combo = main.locator("input[type=search]").last
        kra_combo.click()
        page.wait_for_timeout(500)
        kra_listbox = page.locator("[id^=vs][id$=__listbox]").last
        kra_listbox.get_by_role("option", name="QA Create Template Category " + _SUFFIX, exact=True).click()
        main.locator("input[type=number]").fill("100")
        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(1000)

        main.get_by_role("button", name="Add KPI").click()
        page.wait_for_timeout(500)
        kpi_combo = main.locator("input[type=search]").last
        kpi_combo.click()
        page.wait_for_timeout(500)
        kpi_listbox = page.locator("[id^=vs][id$=__listbox]").last
        kpi_listbox.get_by_role("option", name="QA Create Template Criterion " + _SUFFIX, exact=True).click()
        main.locator("input[type=number]").last.fill("1")
        main.get_by_role("button", name="Add KPI").click()
        page.wait_for_timeout(1000)

        main.get_by_role("button", name="Next Step").click()
        page.wait_for_timeout(1000)
        expect(main.get_by_text("Template is ready to save/publish!")).to_be_visible()
        main.get_by_role("button", name="Save Template").click()

        expect(page.get_by_text("Template created successfully.")).to_be_visible(timeout=10000)
        expect(page).to_have_url("https://organice.qc.iocod.com/reviews/templates")

        search = main.locator("input[placeholder='Search templates...']")
        search.fill("QA Test Template G " + _SUFFIX)
        page.wait_for_timeout(2500)
        row = main.locator(".hidden.lg\\:block div.grid").filter(has_text="QA Test Template G " + _SUFFIX)
        expect(row).to_contain_text("Software Tester")
        expect(row).to_contain_text("1")

        # cleanup: delete the template, then the supporting KRA/KPI (a KRA
        # must be deactivated before it can be deleted)
        row.locator("button").nth(2).click()
        page.wait_for_timeout(500)
        page.get_by_role("button", name="Delete", exact=True).click()
        page.wait_for_timeout(500)
        confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Confirm Delete").first
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Template deleted", exact=False)).to_be_visible(timeout=10000)

        page.get_by_test_id("sidebar-child-template-content").click()
        page.wait_for_timeout(1500)
        search_kra.fill("QA Create Template Category " + _SUFFIX)
        page.wait_for_timeout(1000)
        kra_row = main.get_by_text("QA Create Template Category " + _SUFFIX, exact=True).first.locator("xpath=ancestor::*[6]")
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
