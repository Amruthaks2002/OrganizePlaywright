from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy, policy_card,
    card_meta, select_policy, detail_badges, detail_description, open_edit_form,
    checked_weekends, dialog,
)


def test_create_policy_all_fields():
    """LP-017: name, region, description and weekends are all saved and shown."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name, region="QA Region", description="QA automation policy",
                          weekends=["Saturday", "Sunday"])

            expect(card_meta(policy_card(page, name)).locator("span").first).to_have_text("QA Region")
            select_policy(page, name)
            expect(detail_badges(page)).to_have_text(["Active", "QA Region"])
            expect(detail_description(page)).to_have_text("QA automation policy")

            form = open_edit_form(page, name)
            assert checked_weekends(form) == ["Saturday", "Sunday"]
            form.get_by_role("button", name="Cancel").click()
            expect(dialog(page, "Edit Leave Policy")).to_be_hidden()
        finally:
            delete_policy(page, name)

        browser.close()
