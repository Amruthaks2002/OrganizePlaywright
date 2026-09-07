import time
from playwright.sync_api import sync_playwright
from utils.login_helper import login

def test_ai_out_of_scope():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-navlink-ai assistant").click()
        page.wait_for_url("**/ai**")

        all_responses = page.locator(".assistant-content")
        ai_textarea = page.locator("textarea[placeholder='Ask your AI Assistant...']")

        # --- Ask an out-of-scope question to AI Assistant---
        ai_textarea.click()
        ai_textarea.fill("What's the weather like today in New York?")
        ai_textarea.press("Enter")

        all_responses.last.wait_for(state="visible", timeout=15000)
        ai_response_text = all_responses.last.inner_text().strip()
        print(f"AI Assistant Response (out-of-scope):\n{ai_response_text}")

        assert ai_response_text, "Expected a non-empty response from the AI assistant"

        response_lower = ai_response_text.lower()

        # Assert the assistant correctly declines and redirects to HR topics
        assert "i can only assist you with hr-related queries" in response_lower, (
            f"Expected assistant to decline out-of-scope question with the standard HR message, "
            f"but got: {ai_response_text}"
        )
        assert "leaves" in response_lower, "Expected response to mention 'leaves' as a supported topic"
        assert "attendance" in response_lower, "Expected response to mention 'attendance' as a supported topic"
        assert "work mode" in response_lower, "Expected response to mention 'work mode' as a supported topic"

        # Negative check: make sure it didn't hallucinate actual weather data
        weather_terms = ["degrees", "°", "sunny", "rainy", "cloudy", "forecast", "temperature"]
        assert not any(term in response_lower for term in weather_terms), (
            f"Assistant appears to have hallucinated a weather answer instead of declining: {ai_response_text}"
        )

        browser.close()