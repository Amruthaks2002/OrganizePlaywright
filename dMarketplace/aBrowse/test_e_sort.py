import re

from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, open_browser_as, unique_name, create_file_app, approve_app, give_kudos, download, delete_apps,
    open_marketplace, sort_select, card_names, SORTS,
)


def test_sort():
    """MP-005: Newest first, Most downloaded, Most kudos and Name A–Z each order the list as named."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        alpha, bravo, charlie = f"{prefix} Alpha", f"{prefix} Bravo", f"{prefix} Charlie"
        try:
            ids = {}
            for name in [alpha, bravo, charlie]:
                ids[name] = create_file_app(page, name)
                approve_app(page, ids[name])
                page.wait_for_timeout(1100)  # created_at has 1s resolution
            # downloads: alpha 2, charlie 1, bravo 0 / kudos: bravo 2, charlie 1, alpha 0
            for name in [alpha, alpha, charlie]:
                download(page, ids[name])
            give_kudos(page, ids[bravo])
            give_kudos(page, ids[charlie])
            emp_browser, emp_page = open_browser_as(p, "employee")
            give_kudos(emp_page, ids[bravo])
            emp_browser.close()

            open_marketplace(page, search=prefix)
            assert card_names(page) == [charlie, bravo, alpha], f"Newest first: {card_names(page)}"

            expected = {"downloads": [alpha, charlie, bravo], "kudos": [bravo, charlie, alpha],
                        "name": [alpha, bravo, charlie], "latest": [charlie, bravo, alpha]}
            for value, order in expected.items():
                sort_select(page).select_option(label=SORTS[value])
                page.wait_for_url(re.compile(rf"sort={value}") if value != "latest" else re.compile(r".*"))
                expect(page.get_by_test_id("main-content").locator("a h2").first).to_have_text(order[0])
                assert card_names(page) == order, f"{SORTS[value]}: {card_names(page)}"
        finally:
            delete_apps(page, alpha, bravo, charlie)

        browser.close()
