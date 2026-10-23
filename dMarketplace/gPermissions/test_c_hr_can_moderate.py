from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, open_browser_as, unique_name, create_app, create_live_app, delete_apps, open_marketplace, open_app,
    open_review, review_card, expect_toast, main_content, app_data, history, REVIEW_URL,
)


def test_hr_can_moderate():
    """MP-047: HR can moderate the marketplace: they see the Review queue, approve submissions,
    and get Edit / Remove on other people's apps."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        live, pending = f"{prefix} Live", f"{prefix} Pending"
        try:
            create_live_app(page, live)
            create_app(page, pending)

            hr_browser, hr_page = open_browser_as(p, "hr")
            open_marketplace(hr_page)
            expect(main_content(hr_page).get_by_role("link", name="Review queue")).to_have_attribute("href", REVIEW_URL)

            open_app(hr_page, live)
            expect(main_content(hr_page).get_by_role("link", name="Edit", exact=True)).to_be_visible()
            expect(main_content(hr_page).get_by_role("button", name="Remove", exact=True)).to_be_visible()

            open_review(hr_page)
            review_card(hr_page, pending).get_by_role("button", name="Approve", exact=True).click()
            expect_toast(hr_page, "is now live in the marketplace")
            hr_browser.close()

            assert app_data(page, pending)["status"] == "approved"
            open_app(page, pending)
            approved_by = history(page)[0]
            assert approved_by.startswith("Approved by") and approved_by != "Approved by Admin User", history(page)
        finally:
            delete_apps(page, live, pending)

        browser.close()
