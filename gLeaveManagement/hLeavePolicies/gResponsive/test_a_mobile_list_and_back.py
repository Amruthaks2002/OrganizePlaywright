from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, goto, POLICIES_URL, policy_cards, policy_names,
    policy_card, detail_name, detail_header, main_content,
)


def test_mobile_list_and_back():
    """LP-045: at phone width, choosing a policy shows its details and 'Back to policies' returns to the list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = policy_names(page)[1]

        page.set_viewport_size({"width": 420, "height": 900})
        goto(page, POLICIES_URL)
        back = main_content(page).get_by_role("button", name="Back to policies")
        edit = detail_header(page).get_by_role("button", name="Edit", exact=True)

        expect(policy_cards(page).first).to_be_visible()
        expect(edit).to_be_hidden()
        expect(back).to_be_hidden()

        policy_card(page, name).click()
        expect(detail_name(page)).to_have_text(name)
        expect(edit).to_be_visible()
        expect(back).to_be_visible()
        expect(policy_cards(page).first).to_be_hidden()

        back.click()
        expect(policy_cards(page).first).to_be_visible()
        expect(edit).to_be_hidden()

        browser.close()
