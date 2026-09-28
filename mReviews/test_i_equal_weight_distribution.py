import time
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_equal_weight_distribution():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        login(page)
        _SUFFIX = str(int(time.time() * 1000))[-6:]
        page.get_by_test_id("theme-toggle-button").click()

        # set up a KRA with two criteria so the weight-splitting behavior can
        # be observed independent of whatever pre-existing KRAs already exist
        page.get_by_test_id("sidebar-parent-reviews").click()
        page.get_by_test_id("sidebar-child-template-content").click()
        main = page.get_by_test_id("main-content")

        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(500)
        kra_modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Create New KRA").first
        kra_modal.locator("input[placeholder='e.g., Technical Skills']").fill("QA Weight Test Category " + _SUFFIX)
        kra_modal.get_by_role("button", name="Create KRA").click()
        expect(page.get_by_text("Category created successfully.")).to_be_visible(timeout=10000)

        search = main.locator("input[placeholder*='Search KRAs']")
        search.fill("QA Weight Test Category " + _SUFFIX)
        page.wait_for_timeout(1000)
        kra_text = main.get_by_text("QA Weight Test Category " + _SUFFIX, exact=True).first
        add_kpi_btn = kra_text.locator("xpath=ancestor::*[6]").locator("button[title='Add KPI']")

        for kpi_name in ["QA Weight Criterion One " + _SUFFIX, "QA Weight Criterion Two " + _SUFFIX]:
            add_kpi_btn.click()
            page.wait_for_timeout(500)
            kpi_modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Create New KPI").first
            kpi_modal.locator("input[placeholder='e.g., Code Quality']").fill(kpi_name)
            kpi_modal.get_by_role("button", name="Create KPI").click()
            expect(page.get_by_text("Criterion created successfully.")).to_be_visible(timeout=10000)
            page.wait_for_timeout(500)

        # build a template using this KRA and assign both criteria equal weight (1 and 1)
        page.get_by_test_id("sidebar-child-review-templates").click()
        page.wait_for_timeout(1500)
        main.get_by_role("button", name="New Template").click()
        page.wait_for_timeout(500)

        desig_input = main.locator("input[placeholder='Select designation']")
        desig_input.click()
        page.wait_for_timeout(500)
        listbox = page.locator("[id^=vs][id$=__listbox]").first
        listbox.get_by_role("option", name="Software Tester", exact=True).click()
        main.locator("input[placeholder*='Performance Appraisal Form']").fill("QA Test Template I " + _SUFFIX)
        main.get_by_role("button", name="Next Step").click()
        page.wait_for_timeout(1000)

        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(500)
        kra_combo = main.locator("input[type=search]").last
        kra_combo.click()
        page.wait_for_timeout(500)
        kra_listbox = page.locator("[id^=vs][id$=__listbox]").last
        kra_listbox.get_by_role("option", name="QA Weight Test Category " + _SUFFIX, exact=True).click()
        main.locator("input[type=number]").fill("100")
        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(1000)

        for kpi_name in ["QA Weight Criterion One " + _SUFFIX, "QA Weight Criterion Two " + _SUFFIX]:
            main.get_by_role("button", name="Add KPI").click()
            page.wait_for_timeout(500)
            kpi_combo = main.locator("input[type=search]").last
            kpi_combo.click()
            page.wait_for_timeout(500)
            kpi_listbox = page.locator("[id^=vs][id$=__listbox]").last
            kpi_listbox.get_by_role("option", name=kpi_name, exact=True).click()
            main.locator("input[type=number]").last.fill("1")
            main.get_by_role("button", name="Add KPI").click()
            page.wait_for_timeout(1000)

        expect(main.get_by_text("(1) — 50.0%")).to_have_count(2)

        # cleanup: the template create flow was never saved, so only the
        # supporting KRA/KPIs need to be removed (a KRA must be deactivated
        # before it or its KPIs can be deleted)
        page.get_by_test_id("sidebar-child-template-content").click()
        page.wait_for_timeout(1500)
        search.fill("QA Weight Test Category " + _SUFFIX)
        page.wait_for_timeout(1000)
        kra_row = main.get_by_text("QA Weight Test Category " + _SUFFIX, exact=True).first.locator("xpath=ancestor::*[6]")
        kra_row.locator("button").first.click()  # expand the row
        page.wait_for_timeout(1000)
        kra_row.locator("button").nth(2).click(force=True)
        page.wait_for_timeout(1500)

        for _ in range(2):
            kra_row.locator("button[title='Delete KPI']").first.click()
            page.wait_for_timeout(600)
            confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Are you sure").first
            confirm.get_by_role("button", name="Delete").click()
            expect(page.get_by_text("Criterion deleted successfully.")).to_be_visible(timeout=10000)
            page.wait_for_timeout(500)

        kra_row.locator("button[title='Delete KRA']").click()
        page.wait_for_timeout(600)
        confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Are you sure").first
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Category deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
