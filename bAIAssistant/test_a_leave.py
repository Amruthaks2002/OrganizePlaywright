import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def test_ai_leave():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-navlink-ai assistant").click()
        page.wait_for_url("**/ai**")

        all_responses = page.locator(".assistant-content")
        ai_textarea = page.locator("textarea[placeholder='Ask your AI Assistant...']")

        # --- Ask: leave balance ---
        ai_textarea.click()
        ai_textarea.fill("What is my current leave balance?")
        ai_textarea.press("Enter")

        all_responses.last.wait_for(state="visible", timeout=15000)
        ai_response_text = all_responses.last.inner_text().strip()
        print(f"AI Assistant Response (1):\n{ai_response_text}")

        assert "leave balance" in ai_response_text.lower(), (
            f"Expected response to mention leave balance, but got: {ai_response_text}"
        )

        # --- Parse the leave balance table from THIS response ---
        balance_response = all_responses.last
        rows = balance_response.locator("table tbody tr")
        row_count = rows.count()
        assert row_count > 0, "Expected at least one row in the leave balance table"

        leave_data = {}
        for i in range(row_count):
            cells = rows.nth(i).locator("td")
            leave_type = cells.nth(0).inner_text().strip()
            total = int(cells.nth(1).inner_text().strip())
            taken = int(cells.nth(2).inner_text().strip())
            remaining = int(cells.nth(3).inner_text().strip())
            leave_data[leave_type] = {"total": total, "taken": taken, "remaining": remaining}

        print("Parsed leave data:", leave_data)

        for leave_type, values in leave_data.items():
            expected_remaining = values["total"] - values["taken"]
            assert values["remaining"] == expected_remaining, (
                f"{leave_type}: expected remaining {expected_remaining}, got {values['remaining']}"
            )

        assert "Planned" in leave_data, "Expected 'Planned' leave type in response"
        assert leave_data["Planned"]["remaining"] == 12, (
            f"Expected Planned remaining to be 12, got {leave_data['Planned']['remaining']}"
        )

        # --- Ask: leave history (separate response, no table assumptions) ---
        prev_count = all_responses.count()

        ai_textarea.click()
        ai_textarea.fill("Show me my leave history.")
        ai_textarea.press("Enter")
        time.sleep(4)

        page.wait_for_function(
            """(prevCount) => document.querySelectorAll('.assistant-content').length > prevCount""",
            arg=prev_count
        )

        second_response_text = all_responses.last.inner_text().strip()
        print(f"AI Assistant Response (2):\n{second_response_text}")

        assert "leave history" in second_response_text.lower(), (
            f"Expected response to contain 'leave history', but got: {second_response_text}"
        )

        browser.close()