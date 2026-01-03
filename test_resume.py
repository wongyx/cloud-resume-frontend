import pytest
import re
from playwright.sync_api import Page, expect

API_PATH = "https://cu649u8va9.execute-api.ap-southeast-1.amazonaws.com/visitorCount/increment"
HTML_PATH = "file:///home/kali/Aws/cloud-resume/cloud-resume-frontend/resume.html"

class TestVisitorCounter:

    #Test if API call is successful
    def test_api_called_and_success(self, page: Page):
        # Wait for the POST request triggered by page load
        with page.expect_response(lambda response:
                                  API_PATH in response.url
                                  and response.request.method == "POST") as response_info:
            page.goto(HTML_PATH)

        response = response_info.value

        # Assert HTTP success
        assert response.status == 200

        # Assert response payload is valid JSON
        data = response.json()
        assert "current_count" in data
        assert isinstance(data["current_count"], int)

    # Test if visitor count is showing the same value as data received from API call
    def test_visitor_count_ui_matches_api(self, page: Page):
        api_count = None

        # Capture API response value
        def handle_response(response):
            nonlocal api_count
            if API_PATH in response.url and response.request.method == "POST" and response.status == 200:
                api_count = response.json()["current_count"]

        page.on("response", handle_response)
        page.goto(HTML_PATH)

        # Locate the counter element by data-testid
        counter = page.locator("[data-testid='visitor-count']")

        # Wait until UI shows numeric value
        expect(counter).to_have_text(re.compile(r"\d+"))

        # Compare displayed value with API value
        displayed_value = int(counter.text_content())

        assert api_count is not None
        assert displayed_value == api_count