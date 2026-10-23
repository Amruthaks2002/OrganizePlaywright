import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_probation_reviews, unique_form_title, create_form_api, delete_forms, search_forms,
    form_row, main_content, settle,
)


def test_view_responses_page():
    """PR-006: View Response opens the probation responses page with its filters and table."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_probation_reviews(page)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, type="probation_review")
            search_forms(page, title)

            form_row(page, title).get_by_role("link", name="View Response →").click()
            expect(page).to_have_url(re.compile(rf"/probation-reviews/form/{form['id']}$"))
            settle(page)
            main = main_content(page)
            expect(main.get_by_role("heading", name=f"Probation Reviews: {title}")).to_be_visible()
            expect(main.get_by_role("link", name="← Back to Forms")).to_be_visible()
            expect(main.get_by_role("button", name="Export Excel")).to_be_visible()
            expect(main.get_by_placeholder("All Employees")).to_be_visible()
            expect(main.get_by_placeholder("All Reviewers")).to_be_visible()
            expect(main.locator("th")).to_have_text(
                [re.compile(p, re.I) for p in ["Employee \\(Reviewee\\)", "Designation", "Reviewer", "Submitted At", "Action"]])
            expect(main.get_by_text("No probation reviews found matching the filters.")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
