from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, approve_app, give_kudos, delete_apps, open_trends, trend_tile,
    trending_list, main_content, show_url,
)


def test_counts_follow_submissions():
    """MP-044: submitting an app adds one to 'Pending review'; approving it moves it to
    'Published apps'; kudos add to 'Total kudos' and put the app in today's trending list.
    Removing it puts every count back.

    The counts are marketplace-wide, so this assumes nobody else is submitting or reviewing
    on QC while it runs."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            open_trends(page)
            before = {label: trend_tile(page, label) for label in ["Published apps", "Pending review", "Total kudos"]}

            app_id = create_app(page, name)
            open_trends(page)
            assert trend_tile(page, "Pending review") == before["Pending review"] + 1
            assert trend_tile(page, "Published apps") == before["Published apps"]

            approve_app(page, app_id)
            give_kudos(page, app_id)
            open_trends(page)
            assert trend_tile(page, "Pending review") == before["Pending review"]
            assert trend_tile(page, "Published apps") == before["Published apps"] + 1
            assert trend_tile(page, "Total kudos") == before["Total kudos"] + 1

            main_content(page).get_by_role("button", name="Today", exact=True).click()
            entry = trending_list(page).get_by_role("link").filter(has_text=name)
            expect(entry).to_have_attribute("href", show_url(name))

            delete_apps(page, name)
            open_trends(page)
            after = {label: trend_tile(page, label) for label in before}
            assert after == before, f"counts not restored: {before} -> {after}"
        finally:
            delete_apps(page, name)

        browser.close()
