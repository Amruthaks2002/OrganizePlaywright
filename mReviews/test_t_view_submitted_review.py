import time
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_view_submitted_review():
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
        kra_modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Create New KRA").first
        kra_modal.locator("input[placeholder='e.g., Technical Skills']").fill("QA View Review Category " + _SUFFIX)
        kra_modal.get_by_role("button", name="Create KRA").click()
        expect(page.get_by_text("Category created successfully.")).to_be_visible(timeout=10000)

        search_kra = main.locator("input[placeholder*='Search KRAs']")
        search_kra.fill("QA View Review Category " + _SUFFIX)
        page.wait_for_timeout(1000)
        kra_text = main.get_by_text("QA View Review Category " + _SUFFIX, exact=True).first
        kra_text.locator("xpath=ancestor::*[6]").locator("button[title='Add KPI']").click()
        page.wait_for_timeout(500)
        kpi_modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Create New KPI").first
        kpi_modal.locator("input[placeholder='e.g., Code Quality']").fill("QA View Review Criterion " + _SUFFIX)
        kpi_modal.get_by_role("button", name="Create KPI").click()
        expect(page.get_by_text("Criterion created successfully.")).to_be_visible(timeout=10000)

        page.get_by_test_id("sidebar-child-review-templates").click()
        page.wait_for_timeout(1500)
        main.get_by_role("button", name="New Template").click()
        page.wait_for_timeout(500)
        desig_input = main.locator("input[placeholder='Select designation']")
        desig_input.click()
        page.wait_for_timeout(500)
        listbox = page.locator("[id^=vs][id$=__listbox]").first
        listbox.get_by_role("option", name="Software Engineer", exact=True).click()
        main.locator("input[placeholder*='Performance Appraisal Form']").fill("QA View Review Template " + _SUFFIX)
        main.get_by_role("button", name="Next Step").click()
        page.wait_for_timeout(1000)

        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(500)
        kra_combo = main.locator("input[type=search]").last
        kra_combo.click()
        page.wait_for_timeout(500)
        kra_listbox = page.locator("[id^=vs][id$=__listbox]").last
        kra_listbox.get_by_role("option", name="QA View Review Category " + _SUFFIX, exact=True).click()
        main.locator("input[type=number]").fill("100")
        main.get_by_role("button", name="Add KRA").click()
        page.wait_for_timeout(1000)

        main.get_by_role("button", name="Add KPI").click()
        page.wait_for_timeout(500)
        kpi_combo = main.locator("input[type=search]").last
        kpi_combo.click()
        page.wait_for_timeout(500)
        kpi_listbox = page.locator("[id^=vs][id$=__listbox]").last
        kpi_listbox.get_by_role("option", name="QA View Review Criterion " + _SUFFIX, exact=True).click()
        main.locator("input[type=number]").last.fill("1")
        main.get_by_role("button", name="Add KPI").click()
        page.wait_for_timeout(1000)

        main.get_by_role("button", name="Next Step").click()
        page.wait_for_timeout(1000)
        main.get_by_role("button", name="Save Template").click()
        expect(page.get_by_text("Template created successfully.")).to_be_visible(timeout=10000)

        search = main.locator("input[placeholder='Search templates...']")
        search.fill("QA View Review Template " + _SUFFIX)
        page.wait_for_timeout(2500)
        row = main.locator(".hidden.lg\\:block div.grid").filter(has_text="QA View Review Template " + _SUFFIX)
        row.locator("button").first.click()
        page.wait_for_timeout(500)
        confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Activate Template").first
        confirm.get_by_role("button", name="Activate").click()
        expect(page.get_by_text("activated successfully", exact=False)).to_be_visible(timeout=10000)

        # submit a review, then view it back
        page.get_by_test_id("sidebar-child-team-reviews").click()
        page.wait_for_timeout(1500)
        card_text = main.get_by_text("Arjun A Praji", exact=True).first
        row2 = card_text.locator("xpath=ancestor::*[4]")
        row2.get_by_role("button", name="Review", exact=True).click()
        page.wait_for_timeout(1500)

        main.get_by_role("button", name="Start Review").click()
        page.wait_for_timeout(1000)
        main.get_by_role("button", name="4", exact=True).click()
        main.locator("textarea").fill("Automated QA review - view flow feedback")
        main.get_by_role("button", name="Continue").click()
        page.wait_for_timeout(1000)
        main.get_by_role("button", name="Submit Review", exact=True).click()
        page.wait_for_timeout(1500)

        row2 = card_text.locator("xpath=ancestor::*[4]")
        row2.get_by_role("button", name="View", exact=True).click()
        page.wait_for_timeout(1500)

        expect(main).to_contain_text("4.00")
        main.get_by_role("button", name="KRA 1", exact=False).click()
        page.wait_for_timeout(800)
        expect(main).to_contain_text("Automated QA review - view flow feedback")

        # cleanup: delete the template, then deactivate the supporting KRA/KPI
        # (they cannot be fully deleted once used in a submitted review, since
        # the app restricts deletion to preserve review history)
        page.get_by_test_id("sidebar-child-review-templates").click()
        page.wait_for_timeout(1500)
        search.fill("QA View Review Template " + _SUFFIX)
        page.wait_for_timeout(2500)
        row = main.locator(".hidden.lg\\:block div.grid").filter(has_text="QA View Review Template " + _SUFFIX)
        row.locator("button").nth(2).click()
        page.wait_for_timeout(500)
        page.get_by_role("button", name="Delete", exact=True).click()
        page.wait_for_timeout(500)
        del_confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Confirm Delete").first
        del_confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Template deleted", exact=False)).to_be_visible(timeout=10000)

        # the KRA/KPI now carry review history, so the app blocks their
        # deletion outright ("cannot be deleted" is disabled even when
        # inactive) to preserve records; deactivating them is the closest
        # available cleanup
        page.get_by_test_id("sidebar-child-template-content").click()
        page.wait_for_timeout(1500)
        search_kra.fill("QA View Review Category " + _SUFFIX)
        page.wait_for_timeout(1000)
        kra_row = main.get_by_text("QA View Review Category " + _SUFFIX, exact=True).first.locator("xpath=ancestor::*[6]")
        kra_row.locator("button").nth(2).click(force=True)
        page.wait_for_timeout(1500)
        expect(kra_row).to_contain_text("Inactive")

        browser.close()
