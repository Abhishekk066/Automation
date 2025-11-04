from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF, XPos, YPos
import time
import requests
import os
import sys

def print_flush(text):
    print(text, flush=True)

print_flush("Starting script...")

with open("./found-pass.txt", "r") as file:
    readUser = file.readline().strip()
    readPass = file.readline().strip()
    print_flush("Reading your credentials...")

print_flush("Searching url...")

URL = "https://gnsu.org/ERP/Student/StudentLogin.aspx"
USERNAME = readUser
PASSWORD = readPass
WAIT = 3

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

print_flush("Working on webpage...")
time.sleep(1)
print_flush("Login your credentials")

try:
    driver.get(URL)
    WebDriverWait(driver, WAIT).until(
        EC.visibility_of_element_located((By.ID, "TxtUserName"))
    ).send_keys(USERNAME)
    driver.find_element(By.ID, "TxtPassword").send_keys(PASSWORD)
    driver.find_element(By.NAME, "BtnLoginSubmit").click()

    time.sleep(2)
    WebDriverWait(driver, WAIT).until_not(
        EC.presence_of_element_located((By.CLASS_NAME, "theme-loader"))
    )

    time.sleep(1)
    try:
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_BtnViewProfile"))
        )
        print_flush("Credentials logged in successfully")
    except Exception as e:
        print_flush("Login failed please check your credentials.")
        driver.quit()
        sys.exit()

    time.sleep(1)
    driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_BtnViewProfile").click()
    time.sleep(1)

    print_flush("Retrieving data from webpage...")

    name = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtSName").get_attribute("value")
    rollno = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtAdmission").get_attribute("value")
    email = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtEmailId").get_attribute("value")
    mobile = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_TxtMobileNo").get_attribute("value")
    adhaar = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtAADHARNO").get_attribute("value")
    address = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtPAdd").text.strip().replace("821305", "").replace("BIHAR", "").replace(",", ", ").replace(",  ", ", ").replace(" ,", ",").replace("- ", "-").rstrip(", ").rstrip(",")
    duration = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblDuration").get_attribute("value")
    regNo = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtapplication").get_attribute("value")
    city = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlPCity").find_element(By.CSS_SELECTOR, "option:checked").text
    currentSem = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlSec").find_element(By.CSS_SELECTOR, "option:checked").text
    program = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlClass").find_element(By.CSS_SELECTOR, "option:checked").text
    batch = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlType").find_element(By.CSS_SELECTOR, "option:checked").text
    bldgrp = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlBloodGroup").find_element(By.CSS_SELECTOR, "option:checked").text
    day = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlDobDate").find_element(By.CSS_SELECTOR, "option:checked").text
    month = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlDobMonth").find_element(By.CSS_SELECTOR, "option:checked").text
    year = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlDobYear").find_element(By.CSS_SELECTOR, "option:checked").text
    country = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlPCountry").find_element(By.CSS_SELECTOR, "option:checked").text
    pincode = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtPPin").get_attribute("value")

    rollno = str(rollno).lower()
    data = {
        "Name": name,
        "RollNo": rollno,
        "Email": email,
        "Current Semester": currentSem,
        "Date of birth": f"{day}-{month}-{year}",
        "Mobile": mobile,
        "Adhaar": adhaar,
        "Program": program,
        "Batch": batch,
        "Duration": duration,
        "Reg-No": regNo,
        "Blood Group": bldgrp,
        "Address": address,
        "Pin": pincode,
        "City": city,
        "Country": country
    }

    print_flush("Writing data from webpage...")

    PATH = f"./outputs/{rollno.upper()}"
    os.makedirs(PATH, exist_ok=True)

    OUTPUT_FILE = f"{PATH}/output_text_{rollno}.txt"

    max_key_length = max(len(key) for key in data.keys())
    with open(OUTPUT_FILE, "w") as file:
        for key, value in data.items():
            file.write(f"{key:<{max_key_length}}   :   {value}\n")

    print_flush("Written data successfully!")

    time.sleep(1)
    print_flush("Saving student image from webpage...")
    upper_rollno = str(rollno).upper()
    response = requests.get(f"https://gnsu.org/ERP/Student_Image/{upper_rollno}_s.jpeg", stream=True)

    if response.status_code == 200:
        with open(f"{PATH}/image_{rollno}.png", "wb") as img:
            for chunk in response.iter_content(1024):
                img.write(chunk)
        print_flush(f"Image saved as 'image_{rollno}.png'!")
    else:
        print_flush(f"Failed to download image. Status code: {response.status_code}")

    time.sleep(1)
    print_flush("Forwarding to attendance url webpage...")
    driver.get("https://gnsu.org/ERP/Student/StudentAttendanceReport.aspx")

    time.sleep(1)
    driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnShow").click()
    time.sleep(2)

    print_flush("Taking attendance screenshot...")
    image_element = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Chart1")
    image_element.screenshot(f"{PATH}/attendance_{rollno}.png")
    print_flush(f"Screenshot saved as 'attendance_{rollno}.png'!")


    class CustomPDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "", 23)
            self.cell(0, 25, "Information", border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf = CustomPDF()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_top_margin(5)
    pdf.add_page()

    txt_file_path = f"{PATH}/output_text_{rollno}.txt"
    image_path = f"{PATH}/image_{rollno}.png"

    try:
        x_position = pdf.w - 50
        y_position = 32
        pdf.image(image_path, x=x_position, y=y_position, w=30, h=39)

        with open(txt_file_path, "r") as txt_file:
            content = txt_file.read()

        pdf.set_font("Courier", size=10)
        pdf.multi_cell(0, 10, content)

        output_filename = f"{PATH}/output_text_{rollno}.pdf"
        pdf.output(output_filename)
        print_flush(f"PDF created and saved as {output_filename}")

    except FileNotFoundError as e:
        print_flush(f"Error: The file '{e.filename}' was not found.")
    except Exception as e:
        print_flush(f"An error occurred: {e}")

    time.sleep(1)
    print_flush("Logging out from webpage...")
    driver.find_element(By.ID, "ctl00_lnkLogout").click()
    time.sleep(1)
    print_flush("All Done!")

    savedPath = f"{PATH}/attendance_{rollno}.png"
    image = Image.open(savedPath)
    image = image.convert("RGB")

    draw = ImageDraw.Draw(image)
    font_path = "./Poppins-Medium.ttf"
    try:
        font = ImageFont.truetype(font_path, size=15)
    except OSError:
        print_flush("Font file not found. Using default font.")
        font = ImageFont.load_default()
    text = name

    image.save(savedPath, quality=100, optimize=True)

except Exception as e:
    print_flush(f"Something went wrong: {type(e).__name__}: {e}")

finally:
    driver.quit()
