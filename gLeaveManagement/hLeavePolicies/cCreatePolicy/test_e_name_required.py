from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, open_create_form, name_input, region_input, policy_cards,
    policy_names,
)


def test_name_required():
    """LP-019: the form can't be submitted without a policy name."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        count_before = policy_cards(page).count()

        form = open_create_form(page)
        region_input(form).fill("QA Region")
        form.get_by_role("button", name="Create Policy").click()

        assert name_input(form).evaluate("e => e.validationMessage") != ""
        expect(form).to_be_visible()
        expect(policy_cards(page)).to_have_count(count_before)
        assert all(policy_names(page))

        browser.close()
