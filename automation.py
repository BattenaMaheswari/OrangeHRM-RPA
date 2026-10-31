
import csv
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchWindowException,
    WebDriverException,
    StaleElementReferenceException,
)
BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = BASE_DIR / "employees.csv"
LOG_FILE = BASE_DIR / "automation.log"
SCREENSHOT_FILE = BASE_DIR / "error_screenshot.png"

LOGIN_URL = (
    "https://opensource-demo.orangehrmlive.com/"
    "web/index.php/auth/login"
)

WAIT_TIME = 30
MAX_PAGES = 1000

KEEP_BROWSER_OPEN = True
# login confg

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
    force=True,
)

def make_result(
    success=False,
    status="failed",
    message="Automation failed",
    employee=None,
    total_records=0,
):

    return {
        "success": success,
        "status": status,
        "message": message,
        "employee": employee or {},
        "total_records": total_records,
        "csv_file": str(CSV_FILE),
    }

def create_driver():

    options = Options()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    driver = webdriver.Chrome(options=options)

    logging.info("Chrome browser started")
    logging.info("Browser windows: %s", driver.window_handles)

    return driver


def browser_is_open(driver):

    try:

        return (
            driver is not None
            and len(driver.window_handles) > 0
        )

    except (NoSuchWindowException, WebDriverException):

        return False
#login

def login_to_orangehrm(driver, username, password):

    wait = WebDriverWait(driver, WAIT_TIME)

    logging.info("Opening OrangeHRM login page")

    driver.get(LOGIN_URL)

    username_field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "username")
        )
    )

    password_field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "password")
        )
    )

    username_field.clear()
    username_field.send_keys(username)

    password_field.clear()
    password_field.send_keys(password)

    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type='submit']")
        )
    )

    login_button.click()

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".oxd-sidepanel")
        )
    )

    logging.info("Login successful")

def inspect_pim_menu(driver):

    try:

        menu_items = driver.find_elements(
            By.CSS_SELECTOR,
            ".oxd-sidepanel-body a"
        )

        for item in menu_items:

            logging.info(
                "MENU ITEM: text=%s | href=%s",
                item.text,
                item.get_attribute("href"),
            )

    except Exception:

        logging.exception("Could not inspect PIM menu")

def wait_for_employee_table(driver):

    wait = WebDriverWait(driver, WAIT_TIME)

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".oxd-table")
        )
    )

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".oxd-table-body")
        )
    )

    logging.info("Employee table container is available")

    return True

def open_employee_list(driver):

    wait = WebDriverWait(driver, WAIT_TIME)

    logging.info("Opening PIM menu")

    pim_menu = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//span[normalize-space()='PIM']"
            )
        )
    )

    pim_menu.click()

    logging.info("PIM menu clicked")

    inspect_pim_menu(driver)

    employee_list = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//a[normalize-space()='Employee List']"
            )
        )
    )

    employee_list.click()

    logging.info("Employee List clicked")

    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//h5[contains(normalize-space(), "
                "'Employee Information')]"
            )
        )
    )

    wait_for_employee_table(driver)

    logging.info("Employee List opened successfully")

def reset_employee_filters(driver):

    wait = WebDriverWait(driver, WAIT_TIME)

    wait_for_employee_table(driver)

    reset_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[normalize-space()='Reset']"
            )
        )
    )

    reset_button.click()

    logging.info("Reset button clicked")

    wait_for_employee_table(driver)

    logging.info("Employee search filters reset")

def search_employee_id(driver, employee_id):

    wait = WebDriverWait(driver, WAIT_TIME)

    wait_for_employee_table(driver)

    old_body = driver.find_element(
        By.CSS_SELECTOR,
        ".oxd-table-body"
    )

    old_html = old_body.get_attribute("innerHTML")

    employee_id_field = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//label[normalize-space()='Employee Id']"
                "/following::input[1]"
            )
        )
    )

    employee_id_field.clear()
    employee_id_field.send_keys(str(employee_id))

    search_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[normalize-space()='Search']"
            )
        )
    )

    search_button.click()

    logging.info(
        "Employee search submitted: %s",
        employee_id
    )

    try:

        wait.until(
            lambda d: (
                d.find_element(
                    By.CSS_SELECTOR,
                    ".oxd-table-body"
                ).get_attribute("innerHTML") != old_html
            )
        )

        logging.info("Employee search results updated")

    except TimeoutException:

        logging.exception(
            "Employee search results did not update"
        )

        raise TimeoutException(
            "Employee search did not complete. "
            "Please check the OrangeHRM table."
        )

    wait_for_employee_table(driver)

    rows = driver.find_elements(
        By.CSS_SELECTOR,
        ".oxd-table-body .oxd-table-card"
    )

    logging.info(
        "Search completed. Rows displayed: %s",
        len(rows)
    )

    for row in rows:

        try:

            logging.info(
                "Search result row: %s",
                row.text
            )

        except StaleElementReferenceException:

            logging.warning(
                "A search result row changed during logging"
            )

    return rows

def employee_exists(driver, employee_id):

    rows = driver.find_elements(
        By.CSS_SELECTOR,
        ".oxd-table-body .oxd-table-card"
    )

    for row in rows:

        cells = row.find_elements(
            By.CSS_SELECTOR,
            ".oxd-table-cell"
        )

        if len(cells) > 1:

            displayed_id = cells[1].text.strip()

            if displayed_id == str(employee_id):

                logging.info(
                    "Employee ID already exists: %s",
                    employee_id
                )

                return True

    logging.info(
        "Employee ID not found: %s",
        employee_id
    )

    return False

def add_employee(
    driver,
    first_name,
    last_name,
    employee_id,
):

    wait = WebDriverWait(driver, WAIT_TIME)

    add_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[normalize-space()='Add']"
            )
        )
    )

    add_button.click()

    logging.info("Add Employee page opened")

    first_name_field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "firstName")
        )
    )

    last_name_field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "lastName")
        )
    )

    first_name_field.clear()
    first_name_field.send_keys(first_name)

    last_name_field.clear()
    last_name_field.send_keys(last_name)

    employee_id_field = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//label[normalize-space()='Employee Id']"
                "/following::input[1]"
            )
        )
    )

    employee_id_field.clear()
    employee_id_field.send_keys(str(employee_id))

    logging.info("Employee details entered")

    save_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[normalize-space()='Save']"
            )
        )
    )

    save_button.click()

    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//h6[contains(normalize-space(), "
                "'Personal Details')]"
            )
        )
    )

    logging.info(
        "Employee created successfully: %s",
        employee_id
    )

    return {
        "first_name": first_name,
        "last_name": last_name,
        "employee_id": str(employee_id),
    }

def extract_table_data(driver):

    return driver.execute_script("""
        const table = document.querySelector(".oxd-table");

        if (!table) {
            return {
                headers: [],
                records: [],
                diagnostic: "Table not found"
            };
        }

        const headers = Array.from(
            table.querySelectorAll(
                ".oxd-table-header .oxd-table-header-cell"
            )
        ).map(cell => cell.innerText.trim());

        const rows = Array.from(
            table.querySelectorAll(
                ".oxd-table-body .oxd-table-card"
            )
        );

        const records = rows.map(row => {

            return Array.from(
                row.querySelectorAll(".oxd-table-cell")
            ).map(cell => cell.innerText.trim());

        });

        return {
            headers: headers,
            records: records,
            diagnostic: {
                rowCount: rows.length
            }
        };
    """)


def get_next_page_button(driver):

    selectors = [
        (
            By.CSS_SELECTOR,
            "button.oxd-pagination-page-item--next"
        ),
        (
            By.XPATH,
            "//button[@aria-label='Next' or @title='Next']"
        ),
        (
            By.XPATH,
            "//button[contains(@class, "
            "'oxd-pagination-page-item') "
            "and .//*[contains(@class, 'bi-chevron-right')]]"
        ),
    ]

    for by, selector in selectors:

        buttons = driver.find_elements(by, selector)

        if buttons:
            return buttons[0]

    return None


def is_next_button_disabled(button):

    if not button.is_enabled():
        return True

    disabled = button.get_attribute("disabled")

    aria_disabled = button.get_attribute(
        "aria-disabled"
    )

    class_name = button.get_attribute("class") or ""

    if disabled is not None:
        return True

    if aria_disabled == "true":
        return True

    if "disabled" in class_name.lower():
        return True

    return False

def extract_employee_records(driver):

    logging.info(
        "Starting employee extraction with pagination"
    )

    wait_for_employee_table(driver)

    all_records = []
    headers = []
    page_number = 1
    seen_records = set()

    while page_number <= MAX_PAGES:

        logging.info(
            "Extracting records from page %s",
            page_number
        )

        table_data = extract_table_data(driver)

        current_headers = table_data.get(
            "headers", []
        )

        current_records = table_data.get(
            "records", []
        )

        if not headers and current_headers:
            headers = current_headers

        logging.info(
            "Page %s records found: %s",
            page_number,
            len(current_records)
        )

        # Collect unique employee rows.
        for row in current_records:

            row_key = tuple(row)

            if row_key not in seen_records:

                seen_records.add(row_key)

                all_records.append(row)

        logging.info(
            "Total unique records collected: %s",
            len(all_records)
        )

        # Find Next button.
        next_button = get_next_page_button(driver)

        if next_button is None:

            logging.info(
                "Next button not found. "
                "Pagination completed."
            )

            break

        if is_next_button_disabled(next_button):

            logging.info(
                "Last page reached. Next button disabled."
            )

            break

        # Capture current table content.
        old_body = driver.find_element(
            By.CSS_SELECTOR,
            ".oxd-table-body"
        )

        old_html = old_body.get_attribute(
            "innerHTML"
        )

        next_button.click()

        logging.info(
            "Next button clicked from page %s",
            page_number
        )

        try:

            WebDriverWait(
                driver,
                WAIT_TIME
            ).until(
                lambda d: (
                    d.find_element(
                        By.CSS_SELECTOR,
                        ".oxd-table-body"
                    ).get_attribute("innerHTML")
                    != old_html
                )
            )

        except TimeoutException:

            logging.exception(
                "Next page failed to load"
            )

            raise TimeoutException(
                "Could not load the next employee page."
            )

        page_number += 1

    else:

        logging.warning(
            "Maximum page limit reached: %s",
            MAX_PAGES
        )

    # Remove checkbox and Actions columns.
    keep_indexes = [
        index
        for index, header in enumerate(headers)
        if header.strip() not in ("", "Actions")
    ]

   
    if not headers and all_records:

        max_columns = max(
            len(row) for row in all_records
        )

        headers = [
            f"Column_{index + 1}"
            for index in range(max_columns)
        ]

        keep_indexes = list(range(max_columns))

    if not headers:

        logging.error(
            "No employee table headers found"
        )

        return 0

    csv_headers = [
        headers[index]
        for index in keep_indexes
    ]

    normalized_records = []

    for row in all_records:

        cleaned_row = [
            row[index] if index < len(row) else ""
            for index in keep_indexes
        ]

        normalized_records.append(cleaned_row)

    # Save CSV.
    with open(
        CSV_FILE,
        mode="w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(csv_headers)

        writer.writerows(normalized_records)

    logging.info(
        "CSV saved successfully: %s",
        CSV_FILE
    )

    logging.info(
        "Total pages processed: %s",
        page_number
    )

    logging.info(
        "Total employee records exported: %s",
        len(normalized_records)
    )

    return len(normalized_records)

def logout_from_orangehrm(driver):

    wait = WebDriverWait(driver, WAIT_TIME)

    logging.info("Starting OrangeHRM logout")

    profile_dropdown = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                ".oxd-userdropdown-tab"
            )
        )
    )

    profile_dropdown.click()

    logging.info("Profile dropdown clicked")

    logout_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//a[normalize-space()='Logout']"
            )
        )
    )

    logout_button.click()

    logging.info("Logout option clicked")

    wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "username")
        )
    )

    logging.info("Logout successful")

    return True

def run_employee_automation(
    username,
    password,
    first_name,
    last_name,
    employee_id,
):

    driver = None
    employee_details = {}

    logging.info("========== AUTOMATION STARTED ==========")

    try:

        # Validate dashboard inputs.
        if not all([
            username,
            password,
            first_name,
            last_name,
            employee_id,
        ]):

            return make_result(
                success=False,
                status="failed",
                message="Please fill in all required fields."
            )

        # Start browser.
        driver = create_driver()

        # Login.
        login_to_orangehrm(
            driver,
            username,
            password
        )

        # Open Employee List.
        open_employee_list(driver)

        # Search Employee ID.
        search_employee_id(
            driver,
            employee_id
        )

        # Check duplicate employee.
        if employee_exists(driver, employee_id):

            logging.info(
                "Duplicate employee creation skipped"
            )

            employee_details = {
                "first_name": first_name,
                "last_name": last_name,
                "employee_id": str(employee_id),
            }

            message = (
                f"Employee ID {employee_id} already exists. "
                "Creation skipped."
            )

        else:

            employee_details = add_employee(
                driver,
                first_name,
                last_name,
                employee_id
            )

            message = "Employee created successfully."

        # Open Employee List again.
        open_employee_list(driver)

        # Reset filters.
        reset_employee_filters(driver)

        # Export all pages.
        total_records = extract_employee_records(driver)

        # Logout.
        logout_from_orangehrm(driver)

        logging.info("========== AUTOMATION COMPLETED ==========")

        return make_result(
            success=True,
            status="success",
            message=(
                message
                + " CSV export completed. "
                + "Logout successful."
            ),
            employee=employee_details,
            total_records=total_records
        )

    except Exception as error:

        logging.exception("Automation failed")

        # Save error screenshot.
        try:

            if browser_is_open(driver):

                driver.save_screenshot(
                    str(SCREENSHOT_FILE)
                )

                logging.info(
                    "Error screenshot saved: %s",
                    SCREENSHOT_FILE
                )

            else:

                logging.error(
                    "Browser is already closed. "
                    "Screenshot unavailable."
                )

        except Exception:

            logging.exception(
                "Could not save error screenshot"
            )

        return make_result(
            success=False,
            status="failed",
            message=f"Automation failed: {str(error)}",
            employee=employee_details
        )

    finally:

        if driver is not None and not KEEP_BROWSER_OPEN:

            try:

                if browser_is_open(driver):

                    driver.quit()

                    logging.info("Chrome browser closed")

            except Exception:

                logging.exception(
                    "Error while closing Chrome"
                )
