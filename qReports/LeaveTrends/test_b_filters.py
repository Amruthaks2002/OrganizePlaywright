from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import re
import time

def test_leave_trends_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        reports_btn = page.get_by_test_id("sidebar-parent-reports")
        expect(reports_btn).to_be_visible()
        expect(reports_btn).to_be_enabled()
        reports_btn.click()

        leave_trends = page.get_by_test_id("sidebar-child-leave-trends")
        leave_trends.scroll_into_view_if_needed()
        leave_trends.click()
        time.sleep(2)

        total_leave_days = page.locator("text=TOTAL LEAVE DAYS").locator("xpath=following-sibling::*[1]")
        applications = page.locator("text=APPLICATIONS").locator("xpath=following-sibling::*[1]")
        start_date = page.locator("input[type=date]").nth(0)
        end_date = page.locator("input[type=date]").nth(1)
        employee_search = page.locator(".vs__search")
        policy_select = page.locator("select").nth(0)
        apply_filter = page.get_by_role("button", name="Apply Filter")
        reset_filters = page.get_by_role("button", name="Reset")

        default_total = total_leave_days.inner_text()
        default_applications = applications.inner_text()
        default_start = start_date.input_value()
        default_end = end_date.input_value()

        # --- Date range filter ---
        start_date.fill("2026-01-01")
        end_date.fill("2026-01-31")
        apply_filter.click()
        time.sleep(2)
        assert total_leave_days.inner_text() != default_total, "Total leave days did not change after applying the date range filter."
        assert applications.inner_text() != default_applications, "Applications count did not change after applying the date range filter."

        reset_filters.click()
        time.sleep(2)
        expect(start_date).to_have_value(default_start)
        expect(end_date).to_have_value(default_end)
        expect(total_leave_days).to_have_text(default_total)

        # --- Employee filter ---
        employee_search.click()
        time.sleep(0.5)
        employee_search.fill("admin")
        page.locator("li[role=option]", has_text="Admin User").first.click()
        apply_filter.click()
        time.sleep(2)
        assert total_leave_days.inner_text() != default_total, "Total leave days did not change after filtering by employee."

        reset_filters.click()
        time.sleep(2)
        expect(employee_search).to_have_attribute("placeholder", "All employees")
        expect(total_leave_days).to_have_text(default_total)

        # --- Policy filter ---
        expect(policy_select).to_have_value("All Policies")
        policy_select.select_option(label="Probation")
        apply_filter.click()
        time.sleep(2)
        assert total_leave_days.inner_text() != default_total, "Total leave days did not change after filtering by policy."

        reset_filters.click()
        time.sleep(2)
        expect(policy_select).to_have_value("All Policies")
        expect(total_leave_days).to_have_text(default_total)

        # --- Daily / Monthly toggle ---
        expect(page.get_by_text("Monthly Leave Bar Chart")).to_be_visible()
        page.get_by_role("button", name="Daily", exact=True).click()
        time.sleep(1)
        expect(page.get_by_text("Daily Leave Bar Chart")).to_be_visible()
        page.get_by_role("button", name="Monthly", exact=True).click()
        time.sleep(1)
        expect(page.get_by_text("Monthly Leave Bar Chart")).to_be_visible()

        # --- Bar / Line chart type toggle ---
        bar_btn = page.get_by_role("button", name="Bar", exact=True)
        line_btn = page.get_by_role("button", name="Line", exact=True)
        re_bg_white = re.compile(".*bg-white.*")

        expect(bar_btn).to_have_class(re_bg_white)
        expect(line_btn).not_to_have_class(re_bg_white)

        line_btn.click()
        time.sleep(1)
        expect(line_btn).to_have_class(re_bg_white)
        expect(bar_btn).not_to_have_class(re_bg_white)

        bar_btn.click()
        time.sleep(1)
        expect(bar_btn).to_have_class(re_bg_white)
        expect(line_btn).not_to_have_class(re_bg_white)

        # --- Reset clears every filter together ---
        start_date.fill("2026-01-01")
        end_date.fill("2026-01-31")
        employee_search.click()
        time.sleep(0.5)
        employee_search.fill("admin")
        page.locator("li[role=option]", has_text="Admin User").first.click()
        policy_select.select_option(label="Probation")
        apply_filter.click()
        time.sleep(2)
        assert total_leave_days.inner_text() != default_total, "Filters did not change the totals before reset."

        reset_filters.click()
        time.sleep(2)
        expect(start_date).to_have_value(default_start)
        expect(end_date).to_have_value(default_end)
        expect(employee_search).to_have_attribute("placeholder", "All employees")
        expect(policy_select).to_have_value("All Policies")
        expect(total_leave_days).to_have_text(default_total)
