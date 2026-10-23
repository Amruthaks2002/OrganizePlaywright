from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_field_config, field_row, field_switch, field_counts, counts_from_switches, expect_toast,
    mandatory_fields, restore_mandatory_fields,
)

FIELD = "Blood Group"


def test_make_field_optional():
    """FC-005: switching a mandatory field off marks it Optional, updates the counters and is saved."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = mandatory_fields(page)
        assert snapshot[FIELD], f"{FIELD} should start mandatory"
        try:
            open_field_config(page)

            field_switch(page, FIELD).click()
            expect_toast(page, "Configuration updated successfully.")
            expect(field_switch(page, FIELD)).to_have_attribute("aria-checked", "false")
            expect(field_row(page, FIELD)).to_contain_text("Optional")
            # other tests may toggle fields at the same time, so compare the counters with the switches
            assert field_counts(page) == counts_from_switches(page), (field_counts(page), counts_from_switches(page))

            open_field_config(page)
            expect(field_switch(page, FIELD)).to_have_attribute("aria-checked", "false")
            expect(field_row(page, FIELD)).to_contain_text("Optional")
        finally:
            restore_mandatory_fields(page, snapshot)

        browser.close()
