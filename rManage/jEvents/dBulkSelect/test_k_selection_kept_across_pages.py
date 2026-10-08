from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, open_events, card_boxes, card_titles, card_box, go_to_page, expect_selected, PAGE_SIZE,
)


def test_selection_kept_across_pages():
    """EB-011: the selection is kept by event while paging - a card ticked on page 1 still counts on
    page 2 and is still ticked back on page 1. Read-only: nothing is submitted."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        open_events(page)
        expect(card_boxes(page)).to_have_count(PAGE_SIZE)
        first = card_titles(page)[0]
        card_box(page, first).check()
        expect_selected(page, 1)

        go_to_page(page, 2)
        expect_selected(page, 1)

        go_to_page(page, 1)
        expect(card_box(page, first).first).to_be_checked()
        expect_selected(page, 1)

        browser.close()
