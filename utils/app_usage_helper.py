import json
import re
from datetime import date, datetime, timedelta

from playwright.sync_api import Page, expect
from utils.learning_helper import BASE_URL, open_browser, main_content  # noqa: F401  (re-exported for the tests)
from utils.onboarding_helper import open_browser_as, expect_forbidden  # noqa: F401  (re-exported for the tests)

APP_USAGE_URL = f"{BASE_URL}/manage/app-usage"
ACTIVITIES_URL = f"{APP_USAGE_URL}/activities"
APP_RELEASES_URL = f"{BASE_URL}/manage/app-releases"
USERS_URL = f"{BASE_URL}/users"
SIDEBAR_LINK = "sidebar-navlink-app usage"

PERIODS = [7, 30, 90]
DEFAULT_PERIOD = 30
ACTIVE_DAYS = 30
PLATFORMS = {"android": "Android", "ios": "iOS"}
STATUSES = {"latest": "Up to date", "ahead": "Newer than release", "outdated": "Update available",
            "unsupported": "Below minimum", "unknown": "No release published"}
INSTALL_COLUMNS = ["User", "Platform", "Version", "Device", "Installed", "Last used"]
ACTIVITY_COLUMNS = ["Time", "User", "Activity", "Platform", "Version"]
ACTIVITY_TYPES = {
    "app.opened": "Opened the app",
    "leave.applied": "Applied for leave",
    "leave.cancelled": "Cancelled a leave request",
    "leave.decided": "Decided on a leave request",
    "work_mode.applied": "Applied for a work mode change",
    "work_mode.cancelled": "Cancelled a work mode request",
    "work_mode.decided": "Decided on a work mode request",
    "room.booked": "Booked a meeting room",
    "room.updated": "Changed a room booking",
    "room.cancelled": "Cancelled a room booking",
    "people_portal.raised": "Raised a People Portal query",
    "people_portal.updated": "Updated a People Portal query",
    "people_portal.deleted": "Deleted a People Portal query",
    "people_portal.responded": "Responded to a People Portal query",
    "note.added": "Added a calendar note",
    "note.updated": "Edited a calendar note",
    "note.deleted": "Deleted a calendar note",
    "task.updated": "Updated a task",
    "profile.updated": "Updated their profile",
    "profile.photo_updated": "Changed their profile photo",
    "profile.photo_removed": "Removed their profile photo",
    "profile.password_changed": "Changed their password",
    "ai.asked": "Asked the AI assistant",
    "session.signed_in": "Signed in",
    "session.signed_out": "Signed out",
}
INSTALLS_EMPTY = "No installs match these filters."
ACTIVITIES_EMPTY = "No app activity matches these filters."
ACTIVITIES_PER_PAGE = 25
END_BEFORE_START = "The end date field must be a date after or equal to start date."
RELATIVE_TIME = re.compile(r"(just now|ago)$")


# ---------- navigation / page data ----------

def load(page: Page, url):
    """Full page load (so page_props() is fresh) and wait for the Vue app to render."""
    response = page.goto(url)
    expect(main_content(page).get_by_role("heading").first).to_be_visible()
    return response


def open_app_usage(page: Page):
    page.get_by_test_id(SIDEBAR_LINK).click()
    page.wait_for_url(APP_USAGE_URL)
    expect(heading(page)).to_be_visible()


def heading(page: Page, name="App Usage"):
    return main_content(page).get_by_role("heading", name=name, exact=True)


def page_props(page: Page):
    """The Inertia props the server sent. Only valid right after a full load (load / reload), because
    in-app navigation doesn't refresh the data-page attribute."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def reload_props(page: Page):
    page.reload()
    expect(main_content(page).get_by_role("heading").first).to_be_visible()
    return page_props(page)


def wait_for_visit(page: Page, action, path=APP_USAGE_URL):
    """Runs an action that makes Inertia refetch the page (filters, period, search) and waits for it."""
    with page.expect_response(lambda r: r.url.startswith(path) and r.request.resource_type in ("xhr", "fetch"),
                              timeout=15000):
        action()
    page.wait_for_timeout(300)  # let Vue re-render with the new props


def query_params(page: Page):
    from urllib.parse import urlparse, parse_qs
    return {k: v[0] for k, v in parse_qs(urlparse(page.url).query).items()}


def is_sidebar_active(page: Page):
    return "bg-slate-100" in (page.get_by_test_id(SIDEBAR_LINK).get_attribute("class") or "")


# ---------- KPI cards ----------

def kpi_card(page: Page, label):
    return main_content(page).locator("section").filter(
        has=page.locator("h2", has_text=re.compile(rf"^\s*{re.escape(label)}\s*$", re.I)))


def kpi(page: Page, label):
    """(value, subtitle) of a summary card."""
    card = kpi_card(page, label)
    return card.locator("p").nth(0).inner_text().strip(), card.locator("p").nth(1).inner_text().strip()


def all_kpis(page: Page):
    return {label: kpi(page, label) for label in
            ["Active today", "Active this week", "Installs in use", "On the latest version"]}


# ---------- daily active users ----------

def period_button(page: Page, days):
    return main_content(page).get_by_role("button", name=f"{days} days", exact=True)


def selected_periods(page: Page):
    return [d for d in PERIODS if "bg-white" in (period_button(page, d).get_attribute("class") or "")]


def pick_period(page: Page, days):
    wait_for_visit(page, lambda: period_button(page, days).click())


# ---------- versions / platforms ----------

def versions_section(page: Page):
    return main_content(page).locator("section").filter(
        has=page.locator("h2", has_text=re.compile(r"^\s*Versions in use\s*$", re.I)))


def status_chip(page: Page, status):
    return versions_section(page).get_by_role("button", name=STATUSES[status], exact=True)


def is_chip_active(page: Page, status):
    return "ring-blue-500" in (status_chip(page, status).get_attribute("class") or "")


def release_chip_texts(page: Page):
    return [" ".join(t.split()) for t in versions_section(page).locator("h2 + div > span").all_inner_texts()]


def platform_breakdown(page: Page):
    """{'Android': (count, '100%'), 'iOS': (0, '0%')} from the Platforms card."""
    section = main_content(page).locator("section").filter(
        has=page.locator("h2", has_text=re.compile(r"^\s*Platforms\s*$", re.I)))
    result = {}
    for row in section.locator("dl > div").all():
        m = re.match(r"(\d+)\s*\((\d+%)\)", " ".join(row.locator("dd").inner_text().split()))
        result[row.locator("dt").inner_text().strip()] = (int(m.group(1)), m.group(2))
    return result


# ---------- installs table ----------

def installs_search(page: Page):
    return main_content(page).locator("input[type=search]")


def installs_platform_select(page: Page):
    # the installs table's two pickers are the only selects on the App Usage page
    return main_content(page).locator("select").nth(0)


def installs_status_select(page: Page):
    return main_content(page).locator("select").nth(1)


def installs_count(page: Page):
    """The number in the 'Installs (N)' heading."""
    h = main_content(page).get_by_role("heading", name=re.compile(r"^\s*Installs\s*\(\d+\)\s*$", re.I))
    return int(re.search(r"\((\d+)\)", h.inner_text()).group(1))


def install_rows(page: Page):
    rows = []
    for tr in main_content(page).locator("table tbody tr").all():
        cells = tr.locator("td")
        if cells.count() < 6:
            continue  # the empty-state row
        version = cells.nth(2)
        rows.append({
            "name": cells.nth(0).locator("p").nth(0).inner_text().strip(),
            "email": cells.nth(0).locator("p").nth(1).inner_text().strip(),
            "platform": cells.nth(1).inner_text().strip(),
            "version": version.locator("span.font-mono").inner_text().strip(),
            "status": version.locator("span.rounded-full").inner_text().strip(),
            "device": [t.strip() for t in cells.nth(3).locator("p").all_inner_texts()],
            "installed": cells.nth(4).inner_text().strip(),
            "last_used": cells.nth(5).inner_text().strip(),
            "last_used_title": cells.nth(5).get_attribute("title"),
        })
    return rows


def search_installs(page: Page, text):
    wait_for_visit(page, lambda: installs_search(page).fill(text))


def filter_installs(page: Page, platform=None, status=None):
    if platform is not None:
        wait_for_visit(page, lambda: installs_platform_select(page).select_option(platform))
    if status is not None:
        wait_for_visit(page, lambda: installs_status_select(page).select_option(status))


def all_installs(page: Page):
    """Every install across all pages, read from the server data."""
    load(page, APP_USAGE_URL)
    installs = page_props(page)["installs"]
    data = list(installs["data"])
    for n in range(2, installs["last_page"] + 1):
        load(page, f"{APP_USAGE_URL}?page={n}")
        data += page_props(page)["installs"]["data"]
    return data


def version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


def expected_status(version, release):
    """What the version-status badge should say for an install, given its platform's release."""
    if not release or not release.get("latest_version"):
        return "unknown"
    v = version_tuple(version)
    if v < version_tuple(release["min_version"]):
        return "unsupported"
    if v == version_tuple(release["latest_version"]):
        return "latest"
    return "ahead" if v > version_tuple(release["latest_version"]) else "outdated"


# ---------- recent activity ----------

def recent_activity_section(page: Page):
    return main_content(page).locator("section").filter(
        has=page.locator("h2", has_text=re.compile(r"^\s*Recent activity\s*$", re.I)))


def sentence_part(label):
    """Recent activity writes "Ajith PT opened the app": the label with only its first letter lower-cased."""
    return label[:1].lower() + label[1:]


def recent_activity_items(page: Page):
    items = []
    for li in recent_activity_section(page).locator("li").all():
        line = li.locator("p").nth(0).locator("span")
        meta = li.locator("p").nth(1)
        items.append({
            "name": line.nth(0).inner_text().strip(),
            "action": line.nth(1).inner_text().strip(),
            "platform": meta.inner_text().split("·")[0].strip(),
            "version": meta.locator("span.font-mono").inner_text().strip(),
            "status": meta.locator("span.rounded-full").inner_text().strip(),
            "time": li.locator("time").inner_text().strip(),
            "datetime": li.locator("time").get_attribute("datetime"),
            "title": li.locator("time").get_attribute("title"),
        })
    return items


# ---------- app activity page ----------

def activity_user_input(page: Page):
    return main_content(page).get_by_placeholder("Name or email")


def activity_type_select(page: Page):
    return main_content(page).locator("select").nth(0)


def activity_platform_select(page: Page):
    return main_content(page).locator("select").nth(1)


def from_date(page: Page):
    return main_content(page).locator("input[type=date]").nth(0)


def to_date(page: Page):
    return main_content(page).locator("input[type=date]").nth(1)


def reset_button(page: Page):
    return main_content(page).get_by_role("button", name="Reset", exact=True)


def activity_rows(page: Page):
    rows = []
    for tr in main_content(page).locator("table tbody tr").all():
        cells = tr.locator("td")
        if cells.count() < 5:
            continue  # the empty-state row
        rows.append({
            "time": cells.nth(0).inner_text().strip(),
            "name": cells.nth(1).locator("p").nth(0).inner_text().strip(),
            "email": cells.nth(1).locator("p").nth(1).inner_text().strip(),
            "activity": cells.nth(2).inner_text().strip(),
            "platform": cells.nth(3).inner_text().strip(),
            "version": cells.nth(4).inner_text().strip(),
        })
    return rows


def activity_time(text):
    return datetime.strptime(text, "%d %b %Y, %I:%M:%S %p")


def activities_footer(page: Page):
    """(first, last, total) from 'Showing 1 – 16 of 16 results'."""
    text = " ".join(main_content(page).get_by_text(re.compile(r"Showing")).inner_text().split())
    m = re.search(r"Showing (\d+) – (\d+) of (\d+) results", text)
    assert m, text
    return tuple(int(x) for x in m.groups())


def filter_activities(page: Page, action):
    wait_for_visit(page, action, ACTIVITIES_URL)


def default_date_range(today=None):
    """The App Activity page defaults to the last 30 days, today included."""
    today = today or date.today()
    return (today - timedelta(days=ACTIVE_DAYS - 1)).isoformat(), today.isoformat()


# ---------- profile card ----------

def open_profile_card(page: Page, avatar_button):
    name = re.match(r"View (.+)'s profile", avatar_button.get_attribute("aria-label")).group(1)
    avatar_button.click()
    view_full = page.get_by_role("button", name="View full profile").last
    expect(view_full).to_be_visible()
    return name, view_full


def users_total(page: Page, query=""):
    """The 'of N results' total on the Users page."""
    load(page, f"{USERS_URL}{query}")
    text = main_content(page).get_by_text(re.compile(r"Showing \d+ to \d+ of \d+ results")).inner_text()
    return int(re.search(r"of (\d+) results", text).group(1))
