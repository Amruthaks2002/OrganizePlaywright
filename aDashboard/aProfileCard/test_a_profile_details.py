import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, main_content, ADMIN, EMPLOYEE


def check_profile_card(page, user):
    main = main_content(page)
    expect(main.get_by_role("heading", name=user["name"])).to_be_visible()
    expect(main.get_by_text(user["email"], exact=True)).to_be_visible()
    expect(main.get_by_text("Designation", exact=True)).to_be_visible()
    expect(main.get_by_text(user["designation"], exact=True).first).to_be_visible()
    experience = main.get_by_text("Company Experience", exact=True).locator("xpath=following-sibling::*[1]")
    expect(experience).to_have_text(re.compile(r"^\s*\d+ (years?|months?|days?)( \d+ (months?|days?))?\s*$"))
    # the green online dot on the avatar
    avatar = main.get_by_role("img", name=user["name"]).first
    expect(avatar.locator("xpath=following-sibling::div[contains(@class,'bg-green-500')]")).to_be_visible()


def test_profile_details():
    """DB-001: the profile card shows the signed-in user's name, email, designation, company
    experience and online dot - for admin and for an employee."""
    with sync_playwright() as p:
        for role, user in [("admin", ADMIN), ("employee", EMPLOYEE)]:
            browser, page = open_browser_as(p, role)
            check_profile_card(page, user)
            browser.close()
