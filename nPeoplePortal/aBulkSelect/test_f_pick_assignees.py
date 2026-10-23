from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, select_all, open_assign,
    assignee_chip, assignee_chips, chip_selected, selected_count, distribute_button, ASSIGNEE,
)


def test_pick_assignees():
    """PB-006: clicking an assignee toggles it (and the "n/N selected" counter); Select All picks
    every eligible assignee and Clear drops them all, disabling Distribute again."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_queries(p, prefix)
            open_portal(page, search=prefix)
            select_all(page, 2)
            dialog = open_assign(page)
            _, eligible = selected_count(dialog)

            chip = assignee_chip(dialog, ASSIGNEE)
            chip.click()
            assert chip_selected(chip) and selected_count(dialog) == (1, eligible), selected_count(dialog)
            expect(distribute_button(dialog)).to_be_enabled()
            chip.click()
            assert not chip_selected(chip) and selected_count(dialog) == (0, eligible), selected_count(dialog)
            expect(distribute_button(dialog)).to_be_disabled()

            dialog.get_by_role("button", name="Select All").click()
            assert selected_count(dialog) == (eligible, eligible), selected_count(dialog)
            assert all(chip_selected(c) for c in assignee_chips(dialog).all())
            dialog.get_by_role("button", name="Clear", exact=True).click()
            assert selected_count(dialog) == (0, eligible), selected_count(dialog)
            expect(distribute_button(dialog)).to_be_disabled()
        finally:
            delete_queries(page, prefix)

        browser.close()
