import re

from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, open_browser_as, unique_name, create_app, create_live_app, delete_apps, open_marketplace, open_app,
    main_content, kudos_button, comment_box, show_url, REVIEW_URL, MARKETPLACE_URL,
)

ROLES = ["employee", "team-lead", "project-manager"]


def test_other_roles_ui_blocked():
    """MP-045: employees, team leads and project managers can browse, give kudos and comment, but
    get no Review queue, no Edit / Remove or history on others' apps, and a 403 on the review
    queue, on others' edit pages and on others' unpublished apps."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        live, pending = f"{prefix} Live", f"{prefix} Pending"
        try:
            live_id = create_live_app(page, live)
            create_app(page, pending)

            for role in ROLES:
                role_browser, role_page = open_browser_as(p, role)
                main = main_content(role_page)
                expect(role_page.get_by_test_id("sidebar-navlink-marketplace")).to_be_visible()
                open_marketplace(role_page)
                expect(main.get_by_role("link", name="Review queue"), role).to_have_count(0)
                expect(main.get_by_role("link", name="Submit application"), role).to_be_visible()

                open_app(role_page, live)
                expect(main.get_by_role("link", name="Edit", exact=True), role).to_have_count(0)
                expect(main.get_by_role("button", name="Remove", exact=True), role).to_have_count(0)
                expect(main.get_by_role("heading", name="History"), role).to_have_count(0)
                expect(kudos_button(role_page), role).to_be_visible()
                expect(comment_box(role_page), role).to_be_visible()

                for url in [REVIEW_URL, f"{MARKETPLACE_URL}/{live_id}/edit", show_url(pending)]:
                    response = role_page.goto(url, wait_until="domcontentloaded")
                    assert response.status == 403, f"{role} {url}: expected 403, got {response.status}"
                    expect(role_page).to_have_title(re.compile("Forbidden"))
                role_browser.close()
        finally:
            delete_apps(page, live, pending)

        browser.close()
