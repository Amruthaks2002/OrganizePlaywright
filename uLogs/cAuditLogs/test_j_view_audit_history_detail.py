from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import re
import time


def test_audit_logs_view_audit_history_detail():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-logs").click()
        audit_log_link = page.get_by_test_id("sidebar-child-audit-log")
        audit_log_link.wait_for(state="visible")
        audit_log_link.click()
        page.get_by_text("Track all system changes and user activities").wait_for(state="visible")
        time.sleep(1)

        first_row = page.locator("table tbody tr").first
        row_model = first_row.locator("td").nth(1).text_content().strip()
        row_changes_text = first_row.locator("td").nth(5).text_content().strip()
        row_had_changes = bool(re.search(r"\d+ fields? updated", row_changes_text))

        first_row.get_by_role("button", name="View").click()
        page.get_by_role("heading", name="Audit History").wait_for(state="visible")
        time.sleep(1)

        # header shows the correct entity type and a numeric id
        header_subtitle = page.get_by_text(re.compile(rf"^{re.escape(row_model)} #\d+$")).first
        expect(header_subtitle).to_be_visible()

        # Detailed Changes section and its record count are self-consistent
        expect(page.get_by_text("Detailed Changes")).to_be_visible()
        showing_text = page.get_by_text(re.compile(r"Showing \d+ audit record")).text_content()
        expected_count = int(re.search(r"Showing (\d+)", showing_text).group(1))
        report_cards = page.locator("div.rounded-lg.border.overflow-hidden")
        assert expected_count == report_cards.count()

        # the row we clicked View on was the most recent audit log entry overall,
        # so it is also the most recent (first) audit report for its own entity
        first_report_card = report_cards.first
        expect(first_report_card.get_by_text("Audit Report 1", exact=True)).to_be_visible()

        if row_had_changes:
            expect(first_report_card.get_by_text("No field-level differences for this record.")).not_to_be_visible()
            expect(first_report_card.get_by_role("columnheader", name="Column")).to_be_visible()
            expect(first_report_card.get_by_role("columnheader", name="Old Value")).to_be_visible()
            expect(first_report_card.get_by_role("columnheader", name="New Value")).to_be_visible()
        else:
            expect(first_report_card.get_by_text("No field-level differences for this record.")).to_be_visible()

        # Back To Audit Logs returns to the list page
        page.get_by_role("link", name="Back To Audit Logs").click()
        page.get_by_role("heading", name="Audit Logs").wait_for(state="visible")

        browser.close()
