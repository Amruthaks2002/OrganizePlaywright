import re

from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, ask, reply_text

WEATHER_TERMS = ["degrees", "°", "sunny", "rainy", "cloudy", "forecast", "temperature"]
# the wording varies ("I can only assist you with HR-related queries", "I can only help with HR topics like ...")
HR_ONLY = re.compile(r"only (help|assist)[^.]*\bhr\b", re.I)


def test_out_of_scope():
    """AI-036: An off-topic question (the weather) is declined with the HR-only message listing the supported topics,
    and no weather is made up."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, _ = ask(page, "What's the weather like today in New York?")
        text = reply_text(reply).lower()

        assert HR_ONLY.search(text), f"expected the HR-only message, got: {reply_text(reply)}"
        for topic in ["leave", "attendance", r"work mode|wfh|work(ing)? from home"]:
            assert re.search(topic, text), f"supported topic '{topic}' isn't mentioned"
        assert not any(term in text for term in WEATHER_TERMS), f"made-up weather: {reply_text(reply)}"

        browser.close()
