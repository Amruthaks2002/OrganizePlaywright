from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def test_send_anonymous_message():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        # navigate to the Anonymous Chat menu
        page.get_by_test_id("sidebar-navlink-anonymous chat").click()
        time.sleep(1)

        # copy the public link
        page.get_by_role("button", name="Copy public link").click()
        time.sleep(1)
        public_link = page.evaluate("() => navigator.clipboard.readText()")
        assert public_link.startswith("https://")

        # open the copied public link in a new tab
        chat_tab = context.new_page()

        # the "Delete conversation" step below triggers a native confirm() dialog
        chat_tab.on("dialog", lambda dialog: dialog.accept())

        chat_tab.goto(public_link)
        time.sleep(1)

        # select a member from the available member list
        chat_tab.get_by_text("Choose a person", exact=False).click()
        member_rows = chat_tab.locator("div.max-h-60.overflow-y-auto button")
        member_rows.first.wait_for(state="visible")
        member_rows.first.click()
        time.sleep(1)

        # enter a message in the chat box
        message_text = "Automated anonymous test message"
        chat_tab.locator("textarea").fill(message_text)
        time.sleep(1)

        # send the message
        send_button = chat_tab.get_by_role("button", name="Send anonymously")
        expect(send_button).to_be_enabled()
        send_button.click()

        # verify the message is successfully sent and displayed in the chat
        chat_tab.wait_for_url("**/anonymous-chat/thread/**", timeout=15000)
        expect(chat_tab.get_by_text(message_text)).to_be_visible()

        # verify the chat window (thread) opened successfully
        expect(chat_tab.get_by_text("encrypted & anonymous")).to_be_visible()

        # send another message from the chat form
        second_message_text = "Second automated anonymous test message"
        reply_box = chat_tab.get_by_placeholder("Write a message…")
        reply_box.fill(second_message_text)
        reply_send_button = reply_box.locator("xpath=following-sibling::button[1]")
        expect(reply_send_button).to_be_enabled()
        reply_send_button.click()
        expect(chat_tab.get_by_text(second_message_text)).to_be_visible()

        # click Save link
        save_link_button = chat_tab.get_by_role("button", name="Save link")
        save_link_button.click()

        # verify the link is saved successfully
        expect(chat_tab.get_by_role("button", name="Saved")).to_be_visible()

        # delete the chat
        chat_tab.locator("button[title='Delete conversation']").click()

        # verify the chat is successfully deleted (page resets to the compose form)
        expect(chat_tab.get_by_role("heading", name="Send an anonymous message")).to_be_visible()
        expect(chat_tab.get_by_text(second_message_text)).not_to_be_visible()

        browser.close()
