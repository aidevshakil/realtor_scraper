from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.realtor.ca/", wait_until="domcontentloaded", timeout=120000)
        print("Home page loaded:", page.url)

        try:
            link = page.get_by_role("link", name="Toronto Real Estate")
            link.first.click(timeout=120000)
        except Exception:
            page.goto("https://www.realtor.ca/on/toronto/real-estate", wait_until="domcontentloaded", timeout=120000)

        page.wait_for_load_state("networkidle", timeout=120000)
        print("Current URL:", page.url)
        print("Page title:", page.title())

        screenshot_path = output_dir / "realtor_toronto.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print("Screenshot saved to:", screenshot_path)

        browser.close()


if __name__ == "__main__":
    main()
