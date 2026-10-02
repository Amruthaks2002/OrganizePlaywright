from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_field_config, field_row, field_switch, field_counts, counts_from_switches, expect_toast,
    mandatory_fields, restore_mandatory_fields, OPTIONAL_FIELD,
)


def test_make_field_mandatory():
    """FC-006: switching an optional field on marks it Required, updates the counters and is saved."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = mandatory_fields(page)
        assert not snapshot[OPTIONAL_FIELD], f"{OPTIONAL_FIELD} should start optional"
        try:
            open_field_config(page)

            field_switch(page, OPTIONAL_FIELD).click()
            expect_toast(page, "Configuration updated successfully.")
            expect(field_switch(page, OPTIONAL_FIELD)).to_have_attribute("aria-checked", "true")
            expect(field_row(page, OPTIONAL_FIELD)).to_contain_text("Required")
            # other tests may toggle fields at the same time, so compare the counters with the switches
            assert field_counts(page) == counts_from_switches(page), (field_counts(page), counts_from_switches(page))

            open_field_config(page)
            expect(field_switch(page, OPTIONAL_FIELD)).to_have_attribute("aria-checked", "true")
        finally:
            restore_mandatory_fields(page, snapshot)

        browser.close()
