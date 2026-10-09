from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, approve_app, reject_app, delete_apps, open_marketplace, mine_switch,
    card_names, app_card, STATUS_LABELS,
)


def test_my_submissions():
    """MP-006: the public list shows only approved apps; 'My submissions' also lists your own
    draft, pending and rejected apps, each with its status badge."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        names = {status: f"{prefix} {status}" for status in STATUS_LABELS}
        try:
            create_app(page, names["draft"], submit=False)
            create_app(page, names["submitted"])
            approve_app(page, create_app(page, names["approved"]))
            reject_app(page, create_app(page, names["rejected"]))

            open_marketplace(page, search=prefix)
            assert card_names(page) == [names["approved"]], card_names(page)

            mine_switch(page).click()
            page.wait_for_url("**mine=1**")
            expect(mine_switch(page)).to_have_attribute("aria-checked", "true")
            expect(app_card(page, names["draft"])).to_be_visible()
            assert sorted(card_names(page)) == sorted(names.values()), card_names(page)
            for status, name in names.items():
                expect(app_card(page, name)).to_contain_text(STATUS_LABELS[status])

            mine_switch(page).click()
            expect(mine_switch(page)).to_have_attribute("aria-checked", "false")
            expect(app_card(page, names["draft"])).to_have_count(0)
            assert card_names(page) == [names["approved"]], card_names(page)
        finally:
            delete_apps(page, *names.values())

        browser.close()
