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

