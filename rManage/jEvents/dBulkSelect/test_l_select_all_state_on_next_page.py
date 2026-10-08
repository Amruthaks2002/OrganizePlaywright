from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, open_events, card_boxes, select_all_box, go_to_page, expect_selected, PAGE_SIZE,
)


def test_select_all_state_on_next_page():
    """EB-012: Select All reflects the cards on the current page - after selecting all of page 1,
    page 2's Select All must not show ticked while its cards aren't all selected.

    Known bug: page 2 shows Select All ticked (carried over from page 1) although most of its cards
    are unticked. Read-only: nothing is submitted. This test fails until that's fixed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        open_events(page)
        select_all_box(page).check()
        expect_selected(page, PAGE_SIZE)

        go_to_page(page, 2)
        unticked = card_boxes(page).count() - card_boxes(page).and_(page.locator(":checked")).count()
        assert unticked > 0, "every card on page 2 is already selected - test needs different data"
        expect(select_all_box(page)).not_to_be_checked()

        browser.close()
