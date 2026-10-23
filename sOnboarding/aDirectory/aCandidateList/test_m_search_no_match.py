from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, search_box, candidate_rows, directory_empty_state, main_content, settle


def test_search_no_match():
    """OD-013: a search with no match shows the empty state."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page)

        search_box(page).fill("zzqa-no-such-candidate")
        expect(directory_empty_state(page)).to_be_visible()
        settle(page)
        expect(main_content(page).get_by_text("Try modifying your search text or selecting a different status filter tab.")).to_be_visible()
        expect(candidate_rows(page)).to_have_count(0)

        browser.close()
