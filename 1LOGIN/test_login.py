from playwright.sync_api import Page
BASE_URL = "https://organice.qc.iocod.com/"
DASHBOARD_KEYWORD = "dashboard"
ERROR_MESSAGE = "These credentials do not match our records."

# ---------------- COMMON LOGIN FUNCTION ----------------
def login(page, email, password):
    print("\nOpening login page...")
    page.goto(BASE_URL)
    print(f"Entering Email: {email}")
    page.fill('[data-testid="email-input"]', email)
    print(f"Entering Password: {password}")
    page.fill('[data-testid="password-input"]', password)
    print("Clicking Login button...")
    page.click('[data-testid="sign-in-button"]')


# Valid email and valid password
def test_login_valid_credentials(page: Page):
    print("\nTEST CASE: Valid Email + Valid Password")
    login(page, "admin@example.com", "password")
    page.wait_for_url(f"**/*{DASHBOARD_KEYWORD}*")
    print("Login successful. Dashboard loaded.")
    assert DASHBOARD_KEYWORD in page.url

# invalid email and invalid password
def test_login_invalid_email_invalid_password(page: Page):
    print("\nTEST CASE: Invalid Email + Invalid Password")
    login(page, "wrong@example.com", "wrong123")
    print("Validating error message...")
    page.wait_for_selector(f"text={ERROR_MESSAGE}")
    assert page.is_visible(f"text={ERROR_MESSAGE}")
    print("Correct error message displayed.")


#  Valid email and invalid password
def test_login_valid_email_invalid_password(page: Page):
    print("\nTEST CASE: Valid Email + Invalid Password")
    login(page, "admin@example.com", "wrong123")
    print("Validating error message...")
    page.wait_for_selector(f"text={ERROR_MESSAGE}")
    assert page.is_visible(f"text={ERROR_MESSAGE}")
    print("Correct error message displayed.")


#  Invalid email and valid password
def test_login_invalid_email_valid_password(page: Page):
    print("\nTEST CASE: Invalid Email + Valid Password")
    login(page, "wrong@example.com", "password")
    print("Validating error message...")
    page.wait_for_selector(f"text={ERROR_MESSAGE}")
    assert page.is_visible(f"text={ERROR_MESSAGE}")
    print("Correct error message displayed.")


#  Email is NOT case sensitive
def test_login_email_case_insensitive(page: Page):
    print("\nTEST CASE: Email Case Insensitive Check")
    login(page, "ADMIN@EXAMPLE.COM", "password")
    page.wait_for_url(f"**/*{DASHBOARD_KEYWORD}*")
    print("Login successful with uppercase email.")
    assert DASHBOARD_KEYWORD in page.url


#  Password IS case sensitive
def test_login_password_case_sensitive(page: Page):
    print("\nTEST CASE: Password Case Sensitive Check")
    login(page, "admin@example.com", "Password")
    print("Validating error message...")
    page.wait_for_selector(f"text={ERROR_MESSAGE}")
    assert page.is_visible(f"text={ERROR_MESSAGE}")
    print("Correct error shown for wrong password case.")


#  Empty email and empty password
def test_login_empty_email_and_password(page: Page):
    print("\nTEST CASE: Empty Email + Empty Password")
    page.goto(BASE_URL)
    page.click('[data-testid="sign-in-button"]')
    validation_message = page.locator('[data-testid="email-input"]').evaluate("el => el.validationMessage")
    assert validation_message != ""
    assert page.url == BASE_URL
    print("Submission blocked by required-field validation on email.")


#  Empty email, valid password
def test_login_empty_email_valid_password(page: Page):
    print("\nTEST CASE: Empty Email + Valid Password")
    page.goto(BASE_URL)
    page.fill('[data-testid="password-input"]', "password")
    page.click('[data-testid="sign-in-button"]')
    validation_message = page.locator('[data-testid="email-input"]').evaluate("el => el.validationMessage")
    assert validation_message != ""
    assert page.url == BASE_URL
    print("Submission blocked by required-field validation on email.")


#  Valid email, empty password
def test_login_valid_email_empty_password(page: Page):
    print("\nTEST CASE: Valid Email + Empty Password")
    page.goto(BASE_URL)
    page.fill('[data-testid="email-input"]', "admin@example.com")
    page.click('[data-testid="sign-in-button"]')
    validation_message = page.locator('[data-testid="password-input"]').evaluate("el => el.validationMessage")
    assert validation_message != ""
    assert page.url == BASE_URL
    print("Submission blocked by required-field validation on password.")


#  Malformed email format (missing "@")
def test_login_malformed_email_format(page: Page):
    print("\nTEST CASE: Malformed Email Format")
    login(page, "notanemail", "password")
    validation_message = page.locator('[data-testid="email-input"]').evaluate("el => el.validationMessage")
    assert "@" in validation_message
    assert page.url == BASE_URL
    print("Browser blocked submission due to invalid email format.")


#  Password visibility toggle (eye icon)
def test_login_password_visibility_toggle(page: Page):
    print("\nTEST CASE: Password Visibility Toggle")
    page.goto(BASE_URL)
    password_input = page.locator('[data-testid="password-input"]')
    password_input.fill("secret123")
    assert password_input.get_attribute("type") == "password"

    page.get_by_test_id("toggle-password-visibility").click()
    assert password_input.get_attribute("type") == "text"

    page.get_by_test_id("toggle-password-visibility").click()
    assert password_input.get_attribute("type") == "password"
    print("Password visibility toggled correctly.")


#  "Remember me" checkbox can be checked/unchecked
def test_login_remember_me_checkbox(page: Page):
    print("\nTEST CASE: Remember Me Checkbox")
    page.goto(BASE_URL)
    remember_me = page.locator("input[type='checkbox']")
    assert remember_me.is_checked() is False
    remember_me.check()
    assert remember_me.is_checked() is True
    print("Remember me checkbox toggled correctly.")


#  "Login with Microsoft" button is present and enabled
def test_login_with_microsoft_button_visible(page: Page):
    print("\nTEST CASE: Login with Microsoft Button Visibility")
    page.goto(BASE_URL)
    microsoft_button = page.get_by_role("button", name="Login with Microsoft")
    assert microsoft_button.is_visible()
    assert microsoft_button.is_enabled()
    print("Login with Microsoft button is visible and enabled.")


#  Pressing Enter in the password field submits the form
def test_login_enter_key_submission(page: Page):
    print("\nTEST CASE: Enter Key Submission")
    page.goto(BASE_URL)
    page.fill('[data-testid="email-input"]', "admin@example.com")
    password_input = page.locator('[data-testid="password-input"]')
    password_input.fill("password")
    password_input.press("Enter")
    page.wait_for_url(f"**/*{DASHBOARD_KEYWORD}*")
    assert DASHBOARD_KEYWORD in page.url
    print("Enter key submitted the form successfully.")


#  Leading/trailing whitespace in email is trimmed
def test_login_email_with_whitespace(page: Page):
    print("\nTEST CASE: Email With Leading/Trailing Whitespace")
    login(page, "  admin@example.com  ", "password")
    page.wait_for_url(f"**/*{DASHBOARD_KEYWORD}*")
    assert DASHBOARD_KEYWORD in page.url
    print("Login succeeded after whitespace was trimmed from email.")


#  Logout ends the session and returns to the login page
def test_logout(page: Page):
    print("\nTEST CASE: Logout")
    login(page, "admin@example.com", "password")
    page.wait_for_url(f"**/*{DASHBOARD_KEYWORD}*")

    page.get_by_test_id("user-profile-button").click()
    logout_link = page.get_by_test_id("user-logout-link")
    logout_link.wait_for(state="visible")
    logout_link.click()

    page.locator('[data-testid="email-input"]').wait_for(state="visible")
    assert DASHBOARD_KEYWORD not in page.url
    print("Logout returned the user to the login page.")


#  Visiting a protected route while logged out redirects to login
def test_protected_route_redirects_when_logged_out(page: Page):
    print("\nTEST CASE: Protected Route Redirect When Logged Out")
    page.goto(f"{BASE_URL}dashboard")
    page.locator('[data-testid="email-input"]').wait_for(state="visible")
    assert DASHBOARD_KEYWORD not in page.url
    print("Unauthenticated visit to a protected route redirected to login.")

