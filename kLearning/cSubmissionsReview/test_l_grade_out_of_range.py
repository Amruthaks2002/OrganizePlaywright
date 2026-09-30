from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import settle, open_browser, main_content, open_submissions_review, submission_rows


def test_grade_out_of_range():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)

        submission_rows(page).first.get_by_role("link", name="Grade / Review").click()
        page.wait_for_url("**/submissions/**")
        settle(page)
        review_url = page.url
        grade = main.locator("input[type=number]")

        # the browser's own validation must block the submit, so nothing reaches the learner's record
        assert not grade.evaluate("e => e.form.noValidate"), "Grade form has validation disabled; not safe to submit"

        for value, reason in [("-5", "rangeUnderflow"), ("150", "rangeOverflow")]:
            grade.fill(value)
            assert grade.evaluate(f"e => e.validity.{reason}"), f"Expected {value} to be out of range"
            main.get_by_role("button", name="Submit Review").click()
            assert grade.evaluate("e => e.validationMessage") != "", f"Expected a grade of {value} to be rejected"
            expect(page).to_have_url(review_url)

        browser.close()
