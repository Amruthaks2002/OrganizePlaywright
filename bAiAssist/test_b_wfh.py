import time
from playwright.sync_api import sync_playwright
from utils.login_helper import login

def test_ai_wfh():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-navlink-ai assistant").click()
        page.wait_for_url("**/ai**")

        all_responses = page.locator(".assistant-content")
        ai_textarea = page.locator("textarea[placeholder='Ask your AI Assistant...']")

        # --- Ask: WFH balance ---
        ai_textarea.click()
        ai_textarea.fill("What is my current WFH balance?")
        ai_textarea.press("Enter")

        all_responses.last.wait_for(state="visible", timeout=15000)
        ai_response_text = all_responses.last.inner_text().strip()
        print(f"AI Assistant Response (1):\n{ai_response_text}")

        assert "work from home" in ai_response_text.lower(), (
            f"Expected response to mention 'work from home', but got: {ai_response_text}"
        )

        # --- Parse the work mode table from THIS response ---
        balance_response = all_responses.last
        rows = balance_response.locator("table tbody tr")
        row_count = rows.count()
        assert row_count > 0, "Expected at least one row in the work mode table"

        wfh_data = {}
        for i in range(row_count):
            cells = rows.nth(i).locator("td")
            work_mode = cells.nth(0).inner_text().strip()
            monthly_limit = cells.nth(1).inner_text().strip()
            wfh_data[work_mode] = {"monthly_limit": monthly_limit}

        print("Parsed WFH data:", wfh_data)

        assert "Work From Home" in wfh_data, "Expected 'Work From Home' row in response"
        assert wfh_data["Work From Home"]["monthly_limit"].lower() == "no limit", (
            f"Expected monthly limit to be 'No Limit', got: {wfh_data['Work From Home']['monthly_limit']}"
        )

        # --- Ask: WFH history (separate response, no table assumptions) ---
        prev_count = all_responses.count()

        ai_textarea.click()
        ai_textarea.fill("Show me my WFH history.")
        ai_textarea.press("Enter")
        time.sleep(5)

        page.wait_for_function(
            """(prevCount) => document.querySelectorAll('.assistant-content').length > prevCount""",
            arg=prev_count
        )

        second_response_text = all_responses.last.inner_text().strip()
        print(f"AI Assistant Response (2):\n{second_response_text}")

        assert "wfh" in second_response_text.lower() or "work from home" in second_response_text.lower(), (
            f"Expected response to mention WFH history, but got: {second_response_text}"
        )

        browser.close()