from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, open_create_form, name_input, region_input,
    description_input, active_toggle, checked_weekends, copy_counter,
)


def test_create_form_defaults():
    """LP-015: the Create Policy form opens empty, Active, with no weekends and the warning shown."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        form = open_create_form(page)
        expect(name_input(form)).to_have_value("")
        expect(region_input(form)).to_have_value("")
        expect(description_input(form)).to_have_value("")
        expect(active_toggle(form)).to_be_checked()
        assert checked_weekends(form) == []
        expect(form.get_by_text("No weekends selected. All days will be treated as working days.")).to_be_visible()
        expect(copy_counter(form, "Copy Leave Type")).to_contain_text("0 /")
        expect(copy_counter(form, "Copy Work Mode")).to_contain_text("0 /")
        expect(form.get_by_role("button", name="Cancel")).to_be_visible()
        expect(form.get_by_role("button", name="Create Policy")).to_be_visible()

        browser.close()
