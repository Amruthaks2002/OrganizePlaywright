from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import (open_ai_as_employee, main_content, quick_action, textarea, send_button,
                                       mic_button, WELCOME_API_URL, PLACEHOLDER, DISCLAIMER, TIME_LABEL)


def test_card_layout():
    """AI-006: The welcome card shows the configured description and quick actions in sort order, with a time stamp;
    the input bar has the placeholder, mic and send buttons and the disclaimer."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        welcome = page.request.get(WELCOME_API_URL, headers={"Accept": "application/json"}).json()
        labels = [a["label"] for a in sorted(welcome["actions"], key=lambda a: a["sort_order"])]

        content = main_content(page)
        expect(content.get_by_text("AI Assistant", exact=True).first).to_be_visible()
        expect(content.get_by_text(TIME_LABEL).first).to_be_visible()
        expect(content.get_by_text(welcome["description"])).to_be_visible()
        for label in labels:
            expect(quick_action(page, label)).to_be_visible()
        shown = [t.strip() for t in content.get_by_role("button").all_inner_texts() if t.strip() in labels]
        assert shown == labels, f"quick actions should be in sort order {labels}, got {shown}"

        expect(textarea(page)).to_have_attribute("placeholder", PLACEHOLDER)
        expect(mic_button(page)).to_be_enabled()
        expect(send_button(page)).to_be_disabled()
        expect(content.get_by_text(DISCLAIMER)).to_be_visible()

        browser.close()
