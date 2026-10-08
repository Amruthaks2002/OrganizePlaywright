from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, load, page_props, main_content, activity_rows, activity_type_select,
                                    filter_activities, query_params, ACTIVITIES_URL, ACTIVITY_TYPES,
                                    ACTIVITIES_PER_PAGE, ACTIVITIES_EMPTY)


def test_activity_filter():
    """AL-005: picking an activity lists only that kind of event; a kind with no events shows the empty message."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)
        all_rows = activity_rows(page)
        complete = page_props(page)["activities"]["total"] <= ACTIVITIES_PER_PAGE
        labels = {label: key for key, label in ACTIVITY_TYPES.items()}
        seen = sorted({r["activity"] for r in all_rows})

        for label in seen:
            filter_activities(page, lambda: activity_type_select(page).select_option(labels[label]))
            assert query_params(page).get("action") == labels[label], page.url
            rows = activity_rows(page)
            assert rows and all(r["activity"] == label for r in rows), (label, rows)
            if complete:
                assert len(rows) == len([r for r in all_rows if r["activity"] == label]), label

        unused = [key for key, label in ACTIVITY_TYPES.items() if label not in seen]
        if complete and unused:
            filter_activities(page, lambda: activity_type_select(page).select_option(unused[0]))
            expect(main_content(page).get_by_text(ACTIVITIES_EMPTY)).to_be_visible()
            assert activity_rows(page) == []

        browser.close()
