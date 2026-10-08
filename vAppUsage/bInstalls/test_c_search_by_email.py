from playwright.sync_api import sync_playwright
from utils.app_usage_helper import open_browser, open_app_usage, install_rows, installs_count, search_installs


def test_search_by_email():
    """AI-003: searching a full email (any letter case) finds that person's installs."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        email = install_rows(page)[-1]["email"]

        for term in [email, email.upper(), email.split("@")[0]]:
            search_installs(page, term)
            rows = install_rows(page)
            assert email in [r["email"] for r in rows], (term, rows)
            assert all(term.lower() in (r["name"] + " " + r["email"]).lower() for r in rows), (term, rows)
            assert installs_count(page) == len(rows)

        browser.close()
