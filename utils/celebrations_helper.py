import datetime
import os
import re
import struct
import tempfile
import uuid
import zlib

from playwright.sync_api import Page, expect
from utils.learning_helper import (  # noqa: F401  (re-exported for the tests)
    BASE_URL, open_browser, main_content, expect_toast, settle, goto,
)

CELEBRATIONS_URL = f"{BASE_URL}/celebrations"
TEMPLATES_URL = f"{BASE_URL}/celebration-templates"
ANNIVERSARY_TEMPLATES_URL = f"{TEMPLATES_URL}?type=work_anniversary"
TEST_TEMPLATE_PREFIX = "QA Template"
EMPTY_STATE = "No pending celebrations at the moment."

# the QC site has no way to create a celebration from the UI, and this approved work
# anniversary is the only one in the system, so the list / prepare tests use it
CELEBRATION_ID = 13
EMPLOYEE = "Vidhuprasad C P"
CELEBRATION_DATE = datetime.date(2026, 6, 4)
CELEBRATION_DATE_TEXT = "June 4, 2026"
ORIGINAL_MESSAGE = "Happy 2 year anniversary"
ANNIVERSARY_TEMPLATES = ["1st Work Anniversary", "2nd Work Anniversary", "3rd Work Anniversary",
                         "4th Work Anniversary"]

# templates are rejected unless they're exactly this size (width, height)
TEMPLATE_SIZES = {"birthday": (2160, 3840), "work_anniversary": (1080, 1920)}


def unique_template_name():
    # random suffix so tests running in parallel never pick the same name
    return f"{TEST_TEMPLATE_PREFIX} {uuid.uuid4().hex[:8]}"


def prepare_url(celebration_id=CELEBRATION_ID):
    return f"{CELEBRATIONS_URL}/{celebration_id}/edit"


def list_url(status="", from_date="", to_date="", type=""):
    return f"{CELEBRATIONS_URL}?from_date={from_date}&status={status}&to_date={to_date}&type={type}"


def wide_list_url(status="", type=""):
    # the default range starts today, so the June 2026 celebration needs a wider one
    return list_url(status, "2020-01-01", "2030-12-31", type)


def add_months(day: datetime.date, months):
    # same overflow as JS setMonth / Carbon addMonths: Nov 30 + 3 months -> Mar 2
    year, month = divmod(day.month - 1 + months, 12)
    return datetime.date(day.year + year, month + 1, 1) + datetime.timedelta(days=day.day - 1)


# ---------- test images ----------

def make_png(name, width=1080, height=1920, noise=False, rgb=(40, 90, 200)):
    """Writes a PNG to the temp dir and returns its path; noise=True makes it incompressible (big)."""
    raw = b"".join(b"\x00" + (os.urandom(width * 3) if noise else bytes(rgb) * width) for _ in range(height))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 0 if noise else 9))
           + chunk(b"IEND", b""))
    path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex[:8]}-{name}")
    with open(path, "wb") as f:
        f.write(png)
    return path


def make_text_file(name="not-an-image.txt"):
    path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex[:8]}-{name}")
    with open(path, "w") as f:
        f.write("not an image")
    return path


# ---------- celebrations list ----------

def open_celebrations(page: Page):
    # the Manage group is already expanded when we're on one of its pages
    if not page.get_by_test_id("sidebar-child-celebrations").is_visible():
        page.get_by_test_id("sidebar-parent-manage").click()
    page.get_by_test_id("sidebar-child-celebrations").click()
    page.wait_for_url("**/celebrations")
    settle(page)


def status_filter(page: Page):
    return main_content(page).locator("#status")


def from_date(page: Page):
    return main_content(page).locator("#from_date")


def to_date(page: Page):
    return main_content(page).locator("#to_date")


def type_filter(page: Page):
    return main_content(page).locator("#type")


def celebration_cards(page: Page):
    return main_content(page).locator("div.grid > div.rounded-xl")


def celebration_card(page: Page, name=EMPLOYEE):
    return celebration_cards(page).filter(has=page.get_by_role("heading", name=name, exact=True))


def empty_state(page: Page):
    return main_content(page).get_by_text(EMPTY_STATE)


def expect_celebration_listed(page: Page, listed=True):
    if listed:
        expect(celebration_card(page)).to_be_visible()
    else:
        expect(empty_state(page)).to_be_visible()
        expect(celebration_card(page)).to_have_count(0)


def set_filter_date(page: Page, field, value):
    field.fill(value)
    expect(page).to_have_url(re.compile(rf"{field.get_attribute('id')}={value}"))
    settle(page)


# ---------- prepare celebration ----------

def open_prepare(page: Page, celebration_id=CELEBRATION_ID):
    goto(page, prepare_url(celebration_id))
    expect(main_content(page).get_by_role("heading", name="Prepare Celebration")).to_be_visible()


def section(page: Page, heading):
    # each step is a white card: heading row, then the content
    return main_content(page).locator("h2", has_text=heading).locator("xpath=../..")


def template_options(page: Page):
    return section(page, "Step 2: Select Template").locator("div.cursor-pointer")


def template_option(page: Page, name):
    return template_options(page).filter(has=page.get_by_text(name, exact=True))


def final_image(page: Page):
    return main_content(page).locator("img[alt='Final celebration image']")


def final_image_input(page: Page):
    return main_content(page).locator("input[type=file]:not(#user-image-input)")


def message_box(page: Page):
    return section(page, "Custom Message").locator("textarea")


def save_message(page: Page, text):
    message_box(page).fill(text)
    main_content(page).get_by_role("button", name="Save Message").click()
    expect_toast(page, "Message updated successfully!")


def image_viewer(page: Page, title):
    # previews open in a full-screen overlay with the title and an ✕ button
    return page.locator("div.fixed.inset-0:visible").filter(
        has=page.get_by_role("heading", name=title, exact=True)).last


def backup_final_image(page: Page):
    """Saves the current final image to a temp file so a test can put it back."""
    src = final_image(page).get_attribute("src")
    response = page.request.get(f"{BASE_URL}{src}")
    assert response.ok, f"downloading the final image failed: {response.status}"
    path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex[:8]}-final{os.path.splitext(src)[1]}")
    with open(path, "wb") as f:
        f.write(response.body())
    return path


def upload_final_image(page: Page, path):
    before = final_image(page).get_attribute("src")
    final_image_input(page).set_input_files(path)
    expect_toast(page, "Final celebration image uploaded successfully.")
    expect(final_image(page)).not_to_have_attribute("src", before)


# ---------- templates ----------

def open_templates(page: Page, url=TEMPLATES_URL):
    goto(page, url)
    expect(main_content(page).get_by_role("heading", name=re.compile("Celebration Templates"))).to_be_visible()


def tab(page: Page, name):
    return main_content(page).get_by_role("button", name=re.compile(name))


def expect_tab_active(page: Page, name):
    expect(tab(page, name)).to_have_class(re.compile("from-purple-500"))


def template_cards(page: Page):
    return main_content(page).locator("div.grid > div.rounded-xl")


def template_card(page: Page, name):
    return template_cards(page).filter(has=page.get_by_role("heading", name=name, exact=True))


def template_names(page: Page):
    return [n.strip() for n in template_cards(page).locator("h3").all_inner_texts()]


def add_template_dialog(page: Page):
    return page.locator("div.fixed.inset-0:visible").filter(
        has=page.get_by_role("heading", name="Add New Template")).last


def open_add_template(page: Page):
    main_content(page).get_by_role("button", name=re.compile("Add Template")).click()
    dialog = add_template_dialog(page)
    expect(dialog).to_be_visible()
    return dialog


def fill_template_form(form, name, image=None, description=None):
    form.locator("input[type=text]").fill(name)
    if description is not None:
        form.locator("textarea").fill(description)
    if image:
        form.locator("input[type=file]").set_input_files(image)


def create_template(page: Page, name, kind="birthday", description=""):
    """Creates an active template through the Add Template dialog and leaves the page on its tab."""
    open_templates(page, ANNIVERSARY_TEMPLATES_URL if kind == "work_anniversary" else TEMPLATES_URL)
    dialog = open_add_template(page)
    fill_template_form(dialog, name, make_png(f"{kind}.png", *TEMPLATE_SIZES[kind]), description)
    dialog.get_by_role("button", name="Create Template").click()
    expect_toast(page, "Template created successfully!")
    expect(template_card(page, name)).to_be_visible()


def edit_template_url(page: Page, name):
    return template_card(page, name).locator("a[href$='/edit']").get_attribute("href")


def toggle_template(page: Page, name, action):
    """action: 'Deactivate' or 'Activate'."""
    template_card(page, name).get_by_role("button", name=action, exact=True).click()
    expect_toast(page, f"Template {action.lower()}d successfully!")


def delete_dialog(page: Page):
    return page.locator("div.fixed.inset-0:visible").filter(
        has=page.get_by_role("heading", name="Delete Template?")).last


def delete_templates(page: Page, name):
    """Deletes every template whose name contains `name`, on both tabs (used as test cleanup)."""
    for url in (TEMPLATES_URL, ANNIVERSARY_TEMPLATES_URL):
        open_templates(page, url)
        cards = template_cards(page).filter(has=page.locator("h3", has_text=name))
        for _ in range(10):
            if cards.count() == 0:
                break
            cards.first.get_by_role("button", name="Delete").click()
            delete_dialog(page).get_by_role("button", name="Delete", exact=True).click()
            expect_toast(page, "Template deleted successfully!")
            open_templates(page, url)
        expect(cards).to_have_count(0)
