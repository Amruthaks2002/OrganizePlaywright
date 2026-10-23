from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, page_props, main_content, activity_rows, activities_footer,
                                    activity_time, wait_for_visit, ACTIVITIES_URL, ACTIVITIES_PER_PAGE)


def test_pagination():
    """AL-015: 25 events per page; the footer counts match, and page 2 continues where page 1 stopped.
    With 25 or fewer events there are no page links."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)
        total = page_props(page)["activities"]["total"]
        rows = activity_rows(page)
        main = main_content(page)
        page_two = main.get_by_role("link", name="2", exact=True).or_(main.get_by_role("button", name="2", exact=True))

        assert len(rows) == min(total, ACTIVITIES_PER_PAGE)
        assert activities_footer(page) == (1, len(rows), total)

        if total <= ACTIVITIES_PER_PAGE:
            assert page_two.count() == 0
        else:
            wait_for_visit(page, lambda: page_two.first.click(), ACTIVITIES_URL)
            second = activity_rows(page)
            assert activities_footer(page) == (ACTIVITIES_PER_PAGE + 1, ACTIVITIES_PER_PAGE + len(second), total)
            assert len(second) == min(total - ACTIVITIES_PER_PAGE, ACTIVITIES_PER_PAGE)
            assert activity_time(second[0]["time"]) <= activity_time(rows[-1]["time"])

        browser.close()
