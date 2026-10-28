import re

from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import launch, open_ai, main_content, AI_URL, SIDEBAR_LINK
from utils.login_helper import login


def test_admin_sidebar_navigation():
    """AI-001: Admin opens the AI Assistant from the sidebar - /ai loads with the AI Assistant chat and the link is active."""
    with sync_playwright() as p:
        browser, page = launch(p)
        login(page)

        open_ai(page)

        assert page.url == AI_URL
        expect(main_content(page).get_by_text("AI Assistant", exact=True).first).to_be_visible()
        # the active link is the only one drawn bold on a grey background
        expect(page.get_by_test_id(SIDEBAR_LINK)).to_have_class(re.compile(r"\bfont-semibold\b.*\bbg-slate-100\b"))
        expect(page.get_by_test_id("sidebar-navlink-dashboard")).not_to_have_class(re.compile(r"\bfont-semibold\b"))

        browser.close()
