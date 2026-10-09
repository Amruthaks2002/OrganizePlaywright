import re

from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, create_file_app, delete_apps, open_review, review_card, main_content,
    show_url,
)


def test_queue_card():
    """MP-021: each pending card shows the name (linking to the app), summary, platform and author,
    an 'Open link' for linked apps or 'Verify (size)' for uploaded packages, and Approve / Reject.
    The pending count matches the cards."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        linked, packaged = f"{prefix} Link", f"{prefix} File"
        try:
            create_app(page, linked, short_description="Linked app summary.")
            file_id = create_file_app(page, packaged)
            open_review(page)
            main = main_content(page)

            card = review_card(page, linked)
            expect(card.get_by_role("link", name=linked, exact=True)).to_have_attribute("href", show_url(linked))
            expect(card).to_contain_text("Linked app summary.")
            expect(card).to_contain_text(re.compile(r"Website · by Admin User", re.I))
            expect(card.get_by_role("link", name="Open link")).to_have_attribute(
                "href", f"https://example.com/{show_url(linked).rsplit('/', 1)[1]}")
            for button in ["Approve", "Reject"]:
                expect(card.get_by_role("button", name=button, exact=True)).to_be_visible()

            card = review_card(page, packaged)
            expect(card).to_contain_text(re.compile(r"Plugin · by Admin User", re.I))
            expect(card.get_by_role("link", name="Verify (128 B)")).to_have_attribute(
                "href", re.compile(rf"/marketplace/{file_id}/download$"))

            cards = main.get_by_role("button", name="Approve", exact=True).count()
            pending = main.get_by_text(re.compile(r"^\s*\d+ pending\s*$"))
            expect(pending).to_have_text(re.compile(rf"^\s*{cards} pending\s*$"))
        finally:
            delete_apps(page, linked, packaged)

        browser.close()
