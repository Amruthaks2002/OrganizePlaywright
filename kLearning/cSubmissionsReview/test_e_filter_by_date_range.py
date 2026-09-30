import re
from datetime import datetime
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import settle, open_browser, main_content, open_submissions_review, submission_rows


def test_filter_by_date_range():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)
        rows = submission_rows(page)

        # use the submitted date of the first row, e.g. "7/31/2026, 5:25:50 PM"
        submitted = rows.first.locator("td").nth(2).inner_text().split(",")[0].strip()
        day = datetime.strptime(submitted, "%m/%d/%Y").strftime("%Y-%m-%d")

        dates = main.locator("input[type=date]")
        dates.nth(0).fill(day)
        dates.nth(1).fill(day)
        expect(page).to_have_url(re.compile(rf"date_from={day}&date_to={day}"))
        settle(page)

        assert rows.count() > 0, f"Expected submissions on {day}"
        for i in range(rows.count()):
            expect(rows.nth(i).locator("td").nth(2)).to_contain_text(submitted)

        browser.close()
