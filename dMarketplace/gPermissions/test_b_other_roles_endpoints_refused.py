from playwright.sync_api import sync_playwright
from utils.marketplace_helper import (
    open_browser, open_browser_as, unique_name, create_app, create_live_app, delete_apps, api, app_data, app_payload,
)

ROLES = ["employee", "team-lead", "project-manager"]


def test_other_roles_endpoints_refused():
    """MP-046: direct approve / reject / submit / update / delete / kudos / comment calls by
    employees, team leads and project managers on someone else's app are refused with 403, and
    nothing changes."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        live, pending, draft = f"{prefix} Live", f"{prefix} Pending", f"{prefix} Draft"
        try:
            live_id = create_live_app(page, live)
            pending_id = create_app(page, pending)
            draft_id = create_app(page, draft, submit=False)
            calls = [
                ("POST", f"/marketplace/{pending_id}/approve", None),
                ("POST", f"/marketplace/{pending_id}/reject", {"action_reason": "Not mine to reject."}),
                ("POST", f"/marketplace/{draft_id}/submit", None),
                ("POST", f"/marketplace/{live_id}/update", app_payload(live, short_description="Hijacked.")),
                ("DELETE", f"/marketplace/{live_id}", None),
                ("POST", f"/marketplace/{pending_id}/kudos", None),
                ("POST", f"/marketplace/{pending_id}/comments", {"body": "Comment on a pending app."}),
            ]

            for role in ROLES:
                role_browser, role_page = open_browser_as(p, role)
                for method, path, data in calls:
                    status, body = api(role_page, method, path, data)
                    assert status == 403, f"{role} {method} {path}: expected 403, got {status}"
                role_browser.close()

            states = {name: app_data(page, name) for name in [live, pending, draft]}
            assert states[live]["status"] == "approved", states[live]
            assert states[live]["short_description"] == "Created by the marketplace tests.", states[live]
            assert states[pending]["status"] == "submitted", states[pending]
            assert states[pending]["kudos_count"] == 0 and states[pending]["comments"] == [], states[pending]
            assert states[draft]["status"] == "draft", states[draft]
        finally:
            delete_apps(page, live, pending, draft)

        browser.close()
