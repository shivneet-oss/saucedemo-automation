"""End-to-end automated tests for saucedemo.com based on saucedemo_test_cases.csv."""

import csv
import os
import sys
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright is required. Install it with:")
    print("  pip install playwright")
    print("  python -m playwright install chromium")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "saucedemo_test_cases.csv"
REPORT_PATH = SCRIPT_DIR / "saucedemo_test_report.html"
BASE_URL = "https://www.saucedemo.com"

VALID_USERNAME = "standard_user"
VALID_PASSWORD = "secret_sauce"
LOCKED_USERNAME = "locked_out_user"

IS_CI = bool(os.getenv("CI"))


@dataclass
class TestResult:
    test_id: str
    description: str
    expected: str
    status: str
    actual: str
    priority: str = ""


def load_test_cases(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def save_test_cases(csv_path: Path, test_cases: list[dict]) -> None:
    fieldnames = [
        "Test Case ID",
        "Description",
        "Expected Result",
        "Priority",
        "Status",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_cases)


def fresh_login(page) -> None:
    """Always start from a completely fresh browser context login."""
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    page.locator("#user-name").fill(VALID_USERNAME)
    page.locator("#password").fill(VALID_PASSWORD)
    page.locator("#login-button").click()
    page.wait_for_url("**/inventory.html")


def get_error_message(page) -> str:
    error = page.locator("[data-test='error']")
    if error.is_visible():
        return error.inner_text().strip()
    return ""


def run_test(context, test_id: str) -> tuple[str, str]:
    """Each test gets its own fresh browser page with clean session."""
    page = context.new_page()

    try:
        # ── LOGIN TESTS ──────────────────────────────────────────────
        if test_id == "TC-LOGIN-001":
            page.goto(BASE_URL)
            page.locator("#user-name").fill(VALID_USERNAME)
            page.locator("#password").fill(VALID_PASSWORD)
            page.locator("#login-button").click()
            if "inventory.html" in page.url:
                return "Pass", "User redirected to product catalogue successfully."
            return "Fail", f"Unexpected URL after login: {page.url}"

        if test_id == "TC-LOGIN-002":
            page.goto(BASE_URL)
            page.locator("#user-name").fill(LOCKED_USERNAME)
            page.locator("#password").fill(VALID_PASSWORD)
            page.locator("#login-button").click()
            error = get_error_message(page)
            if "locked out" in error.lower():
                return "Pass", error
            return "Fail", error or "No error message shown for locked user."

        if test_id == "TC-LOGIN-003":
            page.goto(BASE_URL)
            page.locator("#user-name").fill(VALID_USERNAME)
            page.locator("#password").fill("wrongpassword")
            page.locator("#login-button").click()
            error = get_error_message(page)
            if "do not match" in error.lower():
                return "Pass", error
            return "Fail", error or "No error message shown for invalid password."

        if test_id == "TC-LOGIN-004":
            page.goto(BASE_URL)
            page.locator("#password").fill(VALID_PASSWORD)
            page.locator("#login-button").click()
            error = get_error_message(page)
            if "username is required" in error.lower():
                return "Pass", error
            return "Fail", error or "No error message shown for empty username."

        if test_id == "TC-LOGIN-005":
            page.goto(BASE_URL)
            page.locator("#user-name").fill(VALID_USERNAME)
            page.locator("#login-button").click()
            error = get_error_message(page)
            if "password is required" in error.lower():
                return "Pass", error
            return "Fail", error or "No error message shown for empty password."

        # ── PRODUCT TESTS ─────────────────────────────────────────────
        if test_id == "TC-PRODUCTS-001":
            fresh_login(page)
            products = page.locator(".inventory_item")
            count = products.count()
            if count > 0:
                return "Pass", f"{count} products displayed in catalogue."
            return "Fail", "No products found in catalogue."

        if test_id == "TC-PRODUCTS-002":
            fresh_login(page)
            page.locator("[data-test='product-sort-container']").select_option("lohi")
            prices = page.locator(".inventory_item_price").all_inner_texts()
            prices_float = [float(p.replace("$", "")) for p in prices]
            if prices_float == sorted(prices_float):
                return "Pass", f"Products sorted correctly by price low to high: {prices_float}"
            return "Fail", f"Products not sorted correctly: {prices_float}"

        if test_id == "TC-PRODUCTS-003":
            fresh_login(page)
            page.locator(".inventory_item_name").first.click()
            if "inventory-item.html" in page.url or "id=" in page.url:
                item_name = page.locator(".inventory_details_name").inner_text()
                return "Pass", f"Product detail page opened correctly: {item_name}"
            return "Fail", f"Product detail page did not open. URL: {page.url}"

        # ── CART TESTS ────────────────────────────────────────────────
        if test_id == "TC-CART-001":
            fresh_login(page)
            page.locator("[data-test^='add-to-cart']").first.click()
            badge = page.locator(".shopping_cart_badge")
            if badge.is_visible() and badge.inner_text() == "1":
                return "Pass", "Cart badge shows 1 item after adding product."
            return "Fail", f"Cart badge shows: {badge.inner_text() if badge.is_visible() else 'nothing'}"

        if test_id == "TC-CART-002":
            fresh_login(page)
            add_buttons = page.locator("[data-test^='add-to-cart']")
            add_buttons.nth(0).click()
            add_buttons.nth(1).click()
            badge = page.locator(".shopping_cart_badge")
            if badge.is_visible() and badge.inner_text() == "2":
                return "Pass", "Cart badge shows 2 items after adding two products."
            return "Fail", f"Cart badge shows: {badge.inner_text() if badge.is_visible() else 'nothing'}"

        if test_id == "TC-CART-003":
            fresh_login(page)
            page.locator("[data-test^='add-to-cart']").first.click()
            page.locator(".shopping_cart_link").click()
            page.locator("[data-test^='remove']").first.click()
            badge = page.locator(".shopping_cart_badge")
            if not badge.is_visible():
                return "Pass", "Cart badge disappeared after removing the only item."
            return "Fail", f"Cart badge still shows: {badge.inner_text()}"

        # ── CHECKOUT TESTS ────────────────────────────────────────────
        if test_id == "TC-CHECKOUT-001":
            fresh_login(page)
            page.locator("[data-test^='add-to-cart']").first.click()
            page.locator(".shopping_cart_link").click()
            page.locator("[data-test='checkout']").click()
            page.locator("[data-test='firstName']").fill("John")
            page.locator("[data-test='lastName']").fill("Smith")
            page.locator("[data-test='postalCode']").fill("110001")
            page.locator("[data-test='continue']").click()
            page.locator("[data-test='finish']").click()
            header = page.locator(".complete-header")
            if header.is_visible() and "thank you" in header.inner_text().lower():
                return "Pass", f"Order confirmed: {header.inner_text()}"
            return "Fail", "Order confirmation page not shown."

        if test_id == "TC-CHECKOUT-002":
            fresh_login(page)
            page.locator("[data-test^='add-to-cart']").first.click()
            page.locator(".shopping_cart_link").click()
            page.locator("[data-test='checkout']").click()
            page.locator("[data-test='continue']").click()
            error = get_error_message(page)
            if "first name is required" in error.lower():
                return "Pass", error
            return "Fail", error or "No error shown for empty first name."

        if test_id == "TC-CHECKOUT-003":
            fresh_login(page)
            page.locator("[data-test^='add-to-cart']").first.click()
            page.locator(".shopping_cart_link").click()
            page.locator("[data-test='checkout']").click()
            page.locator("[data-test='firstName']").fill("John")
            page.locator("[data-test='continue']").click()
            error = get_error_message(page)
            if "last name is required" in error.lower():
                return "Pass", error
            return "Fail", error or "No error shown for empty last name."

        if test_id == "TC-CHECKOUT-004":
            fresh_login(page)
            page.locator("[data-test^='add-to-cart']").first.click()
            page.locator(".shopping_cart_link").click()
            page.locator("[data-test='checkout']").click()
            page.locator("[data-test='firstName']").fill("John")
            page.locator("[data-test='lastName']").fill("Smith")
            page.locator("[data-test='continue']").click()
            error = get_error_message(page)
            if "postal code is required" in error.lower():
                return "Pass", error
            return "Fail", error or "No error shown for empty postal code."

        # ── LOGOUT TESTS ──────────────────────────────────────────────
        if test_id == "TC-LOGOUT-001":
            fresh_login(page)
            page.locator("#react-burger-menu-btn").click()
            page.locator("#logout_sidebar_link").wait_for(state="visible")
            page.locator("#logout_sidebar_link").click()
            if page.url == BASE_URL + "/" or page.url == BASE_URL:
                return "Pass", "User logged out and redirected to login page."
            return "Fail", f"Unexpected URL after logout: {page.url}"

        return "Skipped", "No automated test defined for this test case."

    finally:
        page.close()


def run_test_case(browser, test_case: dict) -> TestResult:
    test_id = test_case["Test Case ID"]
    description = test_case["Description"]
    expected = test_case["Expected Result"]
    priority = test_case.get("Priority", "")

    # Each test gets its own fresh browser context — completely clean session
    context = browser.new_context()
    try:
        status, actual = run_test(context, test_id)
    finally:
        context.close()

    return TestResult(
        test_id=test_id,
        description=description,
        expected=expected,
        status=status,
        actual=actual,
        priority=priority,
    )


def print_results(results: list[TestResult]) -> None:
    print("=" * 70)
    print("SAUCEDEMO END-TO-END AUTOMATED TEST RESULTS")
    print("=" * 70)

    for index, result in enumerate(results, start=1):
        print(f"\n{index}. {result.test_id} - {result.status}")
        print(f"   Description: {result.description}")
        print(f"   Expected:    {result.expected}")
        print(f"   Actual:      {result.actual}")

    passed = sum(1 for r in results if r.status == "Pass")
    failed = sum(1 for r in results if r.status == "Fail")
    skipped = sum(1 for r in results if r.status == "Skipped")

    print("\n" + "=" * 70)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("=" * 70)


def generate_html_report(results: list[TestResult], report_path: Path) -> None:
    passed = sum(1 for r in results if r.status == "Pass")
    failed = sum(1 for r in results if r.status == "Fail")
    skipped = sum(1 for r in results if r.status == "Skipped")
    total = len(results)
    pass_rate = int((passed / total) * 100) if total > 0 else 0
    timestamp = datetime.now().strftime("%d %B %Y, %I:%M %p")

    rows = ""
    for index, result in enumerate(results, start=1):
        if result.status == "Pass":
            badge = '<span class="badge pass">PASS</span>'
        elif result.status == "Fail":
            badge = '<span class="badge fail">FAIL</span>'
        else:
            badge = '<span class="badge skipped">SKIPPED</span>'

        rows += f"""
        <tr>
            <td>{index}</td>
            <td><strong>{result.test_id}</strong></td>
            <td>{result.description}</td>
            <td>{result.expected}</td>
            <td>{result.actual}</td>
            <td><span class="priority {result.priority.lower()}">{result.priority}</span></td>
            <td>{badge}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SauceDemo Test Report</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: Arial, Helvetica, sans-serif; background: #f4f6f8; color: #1f2937; padding: 30px; }}
        .header {{ background: #e2231a; color: white; padding: 24px 32px; border-radius: 10px; margin-bottom: 24px; }}
        .header h1 {{ font-size: 1.8rem; margin-bottom: 6px; }}
        .header p {{ font-size: 0.9rem; opacity: 0.8; }}
        .summary {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
        .card {{ background: white; border-radius: 10px; padding: 20px 28px; flex: 1; min-width: 140px;
                 box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }}
        .card .number {{ font-size: 2.2rem; font-weight: 700; margin-bottom: 4px; }}
        .card .label {{ font-size: 0.85rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }}
        .card.pass .number {{ color: #059669; }}
        .card.fail .number {{ color: #dc2626; }}
        .card.skipped .number {{ color: #d97706; }}
        .card.total .number {{ color: #2563eb; }}
        .card.rate .number {{ color: #7c3aed; }}
        table {{ width: 100%; border-collapse: collapse; background: white;
                 border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
        thead {{ background: #e2231a; color: white; }}
        th {{ padding: 14px 16px; text-align: left; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        td {{ padding: 14px 16px; border-bottom: 1px solid #f3f4f6; font-size: 0.9rem; vertical-align: top; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background: #f9fafb; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }}
        .badge.pass {{ background: #d1fae5; color: #065f46; }}
        .badge.fail {{ background: #fee2e2; color: #991b1b; }}
        .badge.skipped {{ background: #fef3c7; color: #92400e; }}
        .priority {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }}
        .priority.high {{ background: #fee2e2; color: #991b1b; }}
        .priority.medium {{ background: #fef3c7; color: #92400e; }}
        .priority.low {{ background: #d1fae5; color: #065f46; }}
        .footer {{ text-align: center; margin-top: 24px; font-size: 0.85rem; color: #9ca3af; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛒 SauceDemo End-to-End Test Report</h1>
        <p>Website: saucedemo.com &nbsp;|&nbsp; Executed: {timestamp} &nbsp;|&nbsp; Tool: Playwright + Python</p>
    </div>

    <div class="summary">
        <div class="card total"><div class="number">{total}</div><div class="label">Total</div></div>
        <div class="card pass"><div class="number">{passed}</div><div class="label">Passed</div></div>
        <div class="card fail"><div class="number">{failed}</div><div class="label">Failed</div></div>
        <div class="card skipped"><div class="number">{skipped}</div><div class="label">Skipped</div></div>
        <div class="card rate"><div class="number">{pass_rate}%</div><div class="label">Pass Rate</div></div>
    </div>

    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Test Case ID</th>
                <th>Description</th>
                <th>Expected Result</th>
                <th>Actual Result</th>
                <th>Priority</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>

    <div class="footer">
        <p>Generated automatically by QA Automation Suite &copy; {datetime.now().year}</p>
    </div>
</body>
</html>"""

    with report_path.open("w", encoding="utf-8") as f:
        f.write(html)


def update_csv_statuses(test_cases: list[dict], results: list[TestResult]) -> None:
    result_map = {result.test_id: result.status for result in results}
    for test_case in test_cases:
        test_id = test_case["Test Case ID"]
        if test_id in result_map:
            test_case["Status"] = result_map[test_id]


def main() -> int:
    if not CSV_PATH.exists():
        print(f"Error: test cases file not found at {CSV_PATH}")
        return 1

    test_cases = load_test_cases(CSV_PATH)
    results: list[TestResult] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=IS_CI,
            slow_mo=0 if IS_CI else 800
        )

        for test_case in test_cases:
            print(f"\nRunning: {test_case['Test Case ID']} - {test_case['Description']}")
            results.append(run_test_case(browser, test_case))

        browser.close()

    print_results(results)
    update_csv_statuses(test_cases, results)
    save_test_cases(CSV_PATH, test_cases)
    print(f"\nUpdated statuses in: {CSV_PATH}")

    generate_html_report(results, REPORT_PATH)
    print(f"HTML report generated: {REPORT_PATH}")

    if not IS_CI:
        webbrowser.open(REPORT_PATH.as_uri())
        print("Report opened in your browser!")

    failed = any(result.status == "Fail" for result in results)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
