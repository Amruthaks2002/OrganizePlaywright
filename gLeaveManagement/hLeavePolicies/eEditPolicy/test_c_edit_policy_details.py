from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    open_edit_form, fill_policy_form, expect_toast, policy_card, card_meta, select_policy,
    detail_badges, detail_description,
)


def test_edit_policy_details():
    """LP-034: name, region and description can be updated."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        new_name = f"{name} Edited"
        try:
            create_policy(page, name, region="QA Region", description="Original description")

            form = open_edit_form(page, name)
            fill_policy_form(form, name=new_name, region="Edited Region", description="Edited description")
            form.get_by_role("button", name="Update Policy").click()
            expect_toast(page, "Leave policy updated successfully.")
            expect(form).to_be_hidden()

            expect(policy_card(page, name)).to_have_count(0)
            expect(card_meta(policy_card(page, new_name)).locator("span").first).to_have_text("Edited Region")
            select_policy(page, new_name)
            expect(detail_badges(page)).to_have_text(["Active", "Edited Region"])
            expect(detail_description(page)).to_have_text("Edited description")
        finally:
            delete_policy(page, new_name)
            delete_policy(page, name)

        browser.close()
