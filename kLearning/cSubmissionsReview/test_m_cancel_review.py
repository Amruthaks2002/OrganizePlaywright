from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import settle, open_browser, main_content, open_submissions_review, submission_rows, goto


def test_cancel_review():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)
        list_url = page.url

        row = submission_rows(page).first
        href = row.get_by_role("link", name="Grade / Review").get_attribute("href")
        # compare raw DOM text; the status is capitalised by CSS
        status_before = row.locator("td").nth(3).text_content().strip()
        grade_before = row.locator("td").nth(4).text_content().strip()

        row.get_by_role("link", name="Grade / Review").click()
        page.wait_for_url(href)
        settle(page)
        main.get_by_placeholder("Write constructive evaluation notes here...").fill("QA note that must not be saved")
        main.get_by_role("button", name="Cancel").click()
        settle(page)
        expect(page).not_to_have_url(href)

        # the submission is unchanged
        goto(page, list_url)
        row = submission_rows(page).filter(has=page.locator(f"a[href='{href}']"))
        assert row.locator("td").nth(3).text_content().strip() == status_before
        assert row.locator("td").nth(4).text_content().strip() == grade_before
        goto(page, href)
        expect(main.get_by_placeholder("Write constructive evaluation notes here...")).not_to_have_value("QA note that must not be saved")

        browser.close()
