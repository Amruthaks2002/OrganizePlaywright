from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_progress, progress_url, main_content, progress_rows, progress_row, progress_values,
)


def test_combined_filters():
    """JP-009: search, role and status filters apply together (from the URL) and show in the filter boxes."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page, progress_url(role="team-lead", status="completed"))
        main = main_content(page)

        expect(main.locator(".vs__selected")).to_have_text(["team-lead", "Completed"])
        expect(progress_row(page, "Team Lead User")).to_have_count(1)
        assert {status for *_, status in progress_values(page)} == {"COMPLETED"}

        # Anjana is a team lead, so she doesn't show up when only admins are wanted
        open_progress(page, progress_url(search="Anjana", role="team-lead", status="completed"))
        expect(progress_row(page, "Anjana Anil")).to_have_count(1)
        open_progress(page, progress_url(search="Anjana", role="admin", status="completed"))
        expect(main.get_by_text("No employee onboarding journeys found.")).to_be_visible()
        expect(progress_rows(page)).to_have_count(0)

        browser.close()
