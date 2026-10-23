import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, candidate_rows, main_content


def test_view_progress_link():
    """OD-018: View Progress isn't offered for submitted / in-progress candidates, and on an approved
    candidate it opens their journey progress.

    (The link follows the employee account rather than the status: an older record approved with
    a field still pending has none, and a candidate sent back for correction after approval keeps it.)
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)

        for status in ["submitted", "in_progress"]:
            open_directory(page, status=status)
            expect(candidate_rows(page).first).to_be_visible()
            expect(candidate_rows(page).get_by_role("link", name="View Progress")).to_have_count(0)

        open_directory(page, status="approved")
        links = candidate_rows(page).get_by_role("link", name="View Progress")
        expect(links.first).to_be_visible()

        links.first.click()
        expect(page).to_have_url(re.compile(r"/hr/onboarding/users/\d+/onboarding-progress$"))
        expect(main_content(page).get_by_role("heading", name="Onboarding Progress")).to_be_visible()

        browser.close()
