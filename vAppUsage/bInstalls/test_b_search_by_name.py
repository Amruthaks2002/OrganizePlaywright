from playwright.sync_api import sync_playwright
from utils.app_usage_helper import open_browser, open_app_usage, install_rows, installs_count, search_installs, query_params


def test_search_by_name():
    """AI-002: searching part of a name, in any letter case, keeps only matching installs."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        target = install_rows(page)[0]
        first_name = target["name"].split()[0]

        for term in [first_name.lower(), first_name.upper(), target["name"]]:
            search_installs(page, term)
            assert query_params(page).get("search") == term, page.url
            rows = install_rows(page)
            assert target["email"] in [r["email"] for r in rows], (term, rows)
            for r in rows:
                assert term.lower() in (r["name"] + " " + r["email"]).lower(), (term, r)
            assert installs_count(page) == len(rows)

        browser.close()
