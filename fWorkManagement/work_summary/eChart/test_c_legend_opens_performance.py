import pytest
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, page_props, team_members, team_select, wait_for_chart,
                                       main_content, PERFORMANCE_URL)


def test_legend_opens_performance():
    """WS-037: clicking a user's name in the chart legend opens that user's performance page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        # the legend is drawn on the canvas, so use a one-person team: its only legend entry sits centred under the chart
        team, members = next(((t, m) for t in page_props(page)["teams"] if len(m := team_members(page, t["id"])) == 1),
                             (None, None))
        if not team:
            pytest.skip("no team with exactly one member")
        [(user_id, name)] = members.items()

        wait_for_chart(page, lambda: team_select(page).select_option(str(team["id"])))
        canvas = main_content(page).locator("canvas")
        box = canvas.bounding_box()
        canvas.click(position={"x": box["width"] / 2, "y": box["height"] - 18})

        page.wait_for_url(f"{PERFORMANCE_URL}/{user_id}")
        expect(main_content(page)).to_contain_text("Performance Review")
        expect(main_content(page)).to_contain_text(name)

        browser.close()
