from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, open_marketplace, app_card, main_content, show_url,
)


def test_card_opens_detail():
    """MP-009: a card shows the app's status, platform, category, summary, author and counts, and
    clicking it opens the detail page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            create_live_app(page, name, category="Reporting", short_description="Card summary text.")
            open_marketplace(page, search=name)
            card = app_card(page, name)
            for text in ["Approved", "Website", "Reporting", "Card summary text.", "Admin User"]:
                expect(card).to_contain_text(text)

            card.click()
            page.wait_for_url(show_url(name))
            expect(main_content(page).get_by_role("heading", name=name, exact=True)).to_be_visible()
        finally:
            delete_apps(page, name)

        browser.close()
