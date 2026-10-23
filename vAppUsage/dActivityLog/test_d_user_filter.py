from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, activity_rows, activity_user_input, filter_activities,
                                    activities_footer, query_params, ACTIVITIES_URL)


def test_user_filter():
    """AL-004: the User filter matches part of a name or an email in any letter case, ignoring surrounding spaces."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)
        target = activity_rows(page)[0]
        first_name = target["name"].split()[0]

        for term in [first_name.lower(), f"  {first_name.upper()}  ", target["email"].upper()]:
            filter_activities(page, lambda: activity_user_input(page).fill(term))
            assert query_params(page).get("search", "").strip() == term.strip(), page.url
            rows = activity_rows(page)
            assert target["email"] in [r["email"] for r in rows], (term, rows)
            for r in rows:
                assert term.strip().lower() in (r["name"] + " " + r["email"]).lower(), (term, r)
            assert activities_footer(page)[2] >= len(rows)

        browser.close()
