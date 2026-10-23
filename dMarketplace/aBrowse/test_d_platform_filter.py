import re

from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, open_marketplace, platform_chip, card_names,
    app_card, main_content,
)


def test_platform_filter():
    """MP-004: the platform chips list only apps of that platform, each card shows its platform,
    and 'All platforms' brings everything back."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        website, idea = f"{prefix} Web", f"{prefix} Idea"
        try:
            create_live_app(page, website, platform="web")
            create_live_app(page, idea, platform="idea")
            open_marketplace(page, search=prefix)
            expect(app_card(page, website)).to_contain_text("Website")
            expect(app_card(page, idea)).to_contain_text("Idea")

            platform_chip(page, "Idea").click()
            page.wait_for_url(re.compile(r"platform=idea"))
            expect(main_content(page).get_by_role("heading", name=website)).to_have_count(0)
            assert card_names(page) == [idea], card_names(page)

            platform_chip(page, "Website").click()
            page.wait_for_url(re.compile(r"platform=web\b"))
            expect(main_content(page).get_by_role("heading", name=idea)).to_have_count(0)
            assert card_names(page) == [website], card_names(page)

            platform_chip(page, "All platforms").click()
            expect(app_card(page, idea)).to_be_visible()
            assert sorted(card_names(page)) == sorted([website, idea]), card_names(page)
            assert "platform=" not in page.url, page.url
        finally:
            delete_apps(page, website, idea)

        browser.close()
