# SauceDemo End-to-End Automation Suite

A comprehensive end-to-end test automation framework for the industry-standard SauceDemo e-commerce demo site, built with Python and Playwright, featuring a CI/CD pipeline on GitHub Actions.

## 🛒 About This Project

SauceDemo (saucedemo.com) is the most widely recognised demo application in QA automation — used in interviews and training worldwide. This project demonstrates a complete automated test suite covering login, product catalogue, shopping cart, checkout, and logout flows.

## 🛠️ Technologies Used

- **Python 3.12** — core programming language
- **Playwright** — browser automation and test execution
- **GitHub Actions** — CI/CD pipeline for automated testing
- **SauceDemo** — industry standard e-commerce demo site
- **CSV** — test case management
- **HTML/CSS** — custom test reporting

## 📋 Test Coverage

### Login Feature (5 test cases)
| Test Case | Description | Priority |
|---|---|---|
| TC-LOGIN-001 | Valid login with standard_user | High |
| TC-LOGIN-002 | Login with locked_out_user | High |
| TC-LOGIN-003 | Login with invalid password | High |
| TC-LOGIN-004 | Login with empty username | Medium |
| TC-LOGIN-005 | Login with empty password | Medium |

### Product Catalogue (3 test cases)
| Test Case | Description | Priority |
|---|---|---|
| TC-PRODUCTS-001 | Product catalogue loads after login | High |
| TC-PRODUCTS-002 | Products sort by price low to high | Medium |
| TC-PRODUCTS-003 | Clicking a product opens detail page | Medium |

### Shopping Cart (3 test cases)
| Test Case | Description | Priority |
|---|---|---|
| TC-CART-001 | Add a product to cart | High |
| TC-CART-002 | Add multiple products to cart | High |
| TC-CART-003 | Remove a product from cart | Medium |

### Checkout (4 test cases)
| Test Case | Description | Priority |
|---|---|---|
| TC-CHECKOUT-001 | Complete checkout with valid details | High |
| TC-CHECKOUT-002 | Checkout with empty first name | Medium |
| TC-CHECKOUT-003 | Checkout with empty last name | Medium |
| TC-CHECKOUT-004 | Checkout with empty postal code | Medium |

### Logout (1 test case)
| Test Case | Description | Priority |
|---|---|---|
| TC-LOGOUT-001 | User can logout successfully | High |

## 🚀 How To Run

### Prerequisites
- Python 3.12 or higher
- pip package manager

### Installation

1. Clone the repository:

git clone https://github.com/shivneet-oss/saucedemo-automation.git
cd saucedemo-automation


2. Install Playwright:

pip install playwright
python -m playwright install chromium


3. Run the tests:

python saucedemo_test_runner.py


## 📊 Test Report

After running, a professional HTML report automatically opens in your browser showing:
- Summary dashboard with Total, Passed, Failed, Skipped counts
- Pass rate percentage
- Colour coded PASS/FAIL/SKIPPED badges
- Priority indicators per test case

## ⚙️ CI/CD Pipeline

Every commit to main automatically triggers the GitHub Actions pipeline which:
1. Sets up a fresh Linux environment
2. Installs Python and Playwright
3. Executes all 16 test cases with full test isolation
4. Reports Pass/Fail results

## 🔑 Test Design Highlights

- **Full test isolation** — each test runs in its own fresh browser context
- **End-to-end coverage** — complete user journeys from login to order confirmation
- **Negative testing** — invalid inputs, locked accounts, empty fields
- **Automatic reporting** — HTML report and CSV status update on every run

## 👤 Author

**Shivneet**
QA Test Manager | 25 years experience
Learning AI-assisted test automation

---
*Built with Python, Playwright and Claude AI assistance*