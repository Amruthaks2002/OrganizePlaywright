from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
from datetime import datetime
import time


def wait_for_message(page, text, timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_preparation_materials():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        sessions_btn = page.get_by_test_id("sidebar-parent-sessions")
        expect(sessions_btn).to_be_visible()
        expect(sessions_btn).to_be_enabled()
        sessions_btn.click()

        knowledge_hub = page.get_by_test_id("sidebar-child-all-sessions")
        knowledge_hub.wait_for(state="visible")
        knowledge_hub.scroll_into_view_if_needed()
        knowledge_hub.click()

        page.get_by_placeholder("Topic, presenter, description...").fill("Automated")
        time.sleep(1)

        with open("session_name.txt", "r") as f:
            session_name = f.read().strip()

        session_link = page.get_by_text(session_name, exact=False).first
        session_link.wait_for(state="visible")
        session_link.click()
        page.wait_for_url("**/sessions/**")
        time.sleep(3)

        prep_card = page.locator("div", has_text="Preparation Materials").filter(
            has=page.get_by_role("button", name="+ Add")
        ).last
        prep_card.get_by_role("button", name="+ Add").click()
        page.get_by_text("Upload Material").wait_for(state="visible")

        # upload file from Downloads
        page.locator("input[type='file']").set_input_files("/Users/amruthaks/Downloads/file_sample.doc")

        prep_label = f"Automated label {datetime.now().strftime('%H%M%S')}"
        page.get_by_placeholder("e.g. Session Slides, Recording Part 1…").fill(prep_label)
        page.get_by_role("button", name="Post Material").click()
        time.sleep(5)

        # deleting the preparation material just added
        prep_row = page.locator("div", has_text=prep_label).filter(
            has=page.get_by_role("button", name="Delete")
        ).last
        prep_row.get_by_role("button", name="Delete").click()

        page.get_by_role("heading", name="Delete Media").last.wait_for(state="visible")
        confirm_modal = page.locator("div.z-\\[10000\\]").last
        confirm_modal.get_by_role("button", name="Delete").click()
        wait_for_message(page, "File deleted successfully.")
        time.sleep(2)

        post_card = page.locator("div", has_text="Post-Session Resources").filter(
            has=page.get_by_role("button", name="+ Add")
        ).last
        post_card.get_by_role("button", name="+ Add").click()
        page.get_by_text("Upload Material").wait_for(state="visible")

        # upload file from Downloads
        page.locator("input[type='file']").set_input_files("/Users/amruthaks/Downloads/file_sample.doc")

        page.get_by_placeholder("e.g. Session Slides, Recording Part 1…").fill("Automated label")
        page.get_by_role("button", name="Post Material").click()
        time.sleep(5)

        browser.close()