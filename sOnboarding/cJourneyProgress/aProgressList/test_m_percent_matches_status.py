from playwright.sync_api import sync_playwright
from utils.onboarding_helper import open_browser, open_progress, progress_url, progress_values


def test_percent_matches_status():
    """JP-013: on every page the % matches the steps completed, 100% is always COMPLETED and
    anything less is IN PROGRESS."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        for page_number in range(1, 4):
            open_progress(page, f"{progress_url()}&page={page_number}")
            for percent, done, total, status in progress_values(page):
                assert percent == round(100 * done / total), (percent, done, total)
                assert status == ("COMPLETED" if done == total else "IN PROGRESS"), (percent, done, total, status)

        browser.close()
