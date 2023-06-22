import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
from bs4 import BeautifulSoup
import chardet
import re
import pandas as pd
import subprocess

# Initialize WebDriver
chrome_options = Options()
webdriver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Path to the folder containing PDFs
pdf_folder_path = "E:/2BVision/PDF_classification/New_Data/Respiratory_Pathogen_Panel_Report"

# Loop through each file in the folder
all_data = []
for file_name in os.listdir(pdf_folder_path):
    if file_name.endswith(".pdf"):
        file_path = os.path.join(pdf_folder_path, file_name)
        
        # Convert PDF to text
        subprocess.run(['pdftotext', '-layout', '-nopgbrk', file_path, 'input.txt'])

        # Detect the encoding of the input file
        with open('input.txt', 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']

        # Open the input file with detected encoding
        with open('input.txt', 'r', encoding=encoding, errors='ignore') as f:
            text = f.read()

            pattern = r'Patient Name.*?\n\n'
            matches = re.search(pattern, text, re.DOTALL)
            data = matches.group()

            summry_pattern = r'Positive for:.*?\n\n'
            summry_pattern_matches = re.search(summry_pattern, text, re.DOTALL)
            if summry_pattern_matches is not None:
                summrydata = summry_pattern_matches.group()
            else:
                summrydata = ""

        # Remove extra spaces and newlines
        cleaned_text = re.sub(r'\s+', ' ', data.strip())

        # Navigate to the chatbot page
        driver.get("https://chat.lmsys.org/")
        wait = WebDriverWait(driver, 30)

        try:
            time.sleep(10)
            search_bar = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="component-10"]/label/textarea')))
            search_bar.send_keys(f'extract the information in bullet form {cleaned_text}')
            time.sleep(5)
        except TimeoutException:
            driver.refresh()

        # Click the send button
        send_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="component-13"]')))
        send_button.click()

        time.sleep(40)

        # Extract the response paragraph
        data_paragraph = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="chatbot"]/div[2]/div/div[2]')))
        time.sleep(3)

        # Parse the HTML content
        soup = BeautifulSoup(data_paragraph.get_attribute("innerHTML"), "html.parser")
        text = soup.get_text()
        lines = text.split('\n')

        if not text.strip():
            print("No text found, refreshing the page")
            driver.refresh()

        # Parsing lines into a dictionary
        data = {}
        for line in lines:
            if ": " in line:
                key, value = line.split(": ", 1)
                data[key] = value
            else:
                print(f"Skipping line: {line}")

        # Converting dictionary into a DataFrame and append it to all_data
        df = pd.DataFrame([data])

        if summrydata:
            df['Target Results'] = summrydata
        else:
            # Add a 'Target Results' column with value 'Not Detected'
            df['Target Results'] = 'Not Detected'

        all_data.append(df)

# Concatenate all data frames
final_df = pd.concat(all_data, ignore_index=True)

# Write the final DataFrame to a CSV file
final_df.to_csv('output.csv', index=False)

# Printing the final DataFrame
print(final_df)











########### Version 1 #############################
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.firefox import GeckoDriverManager
# from selenium.common.exceptions import TimeoutException
# import time
# from bs4 import BeautifulSoup
# import chardet
# import re
# import pandas as pd
# import subprocess


# # Initialize WebDriver
# chrome_options = Options()
# webdriver_service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)


# # Convert PDF to text
# file = "test (2).pdf"
# subprocess.run(['pdftotext', '-layout', '-nopgbrk', file, 'input.txt'])

# # Detect the encoding of the input file
# with open('input.txt', 'rb') as f:
#     result = chardet.detect(f.read())
# encoding = result['encoding']

# # Open the input file with detected encoding
# with open('input.txt', 'r', encoding=encoding, errors='ignore') as f:
#     text = f.read()

#     pattern = r'Patient Name.*?\n\n'
#     matches = re.search(pattern, text, re.DOTALL)
#     data = matches.group()

#     summry_pattern = r'Positive for:.*?\n\n'
#     summry_pattern_matches = re.search(summry_pattern, text, re.DOTALL)
#     if summry_pattern_matches is not None:
#         summrydata = summry_pattern_matches.group()
#     else:
#         summrydata = ""


# # Remove extra spaces and newlines
# cleaned_text = re.sub(r'\s+', ' ', data.strip())

# # Navigate to the chatbot page
# driver.get("https://chat.lmsys.org/")
# wait = WebDriverWait(driver, 30)

# try:
#     time.sleep(10)
#     search_bar = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="component-10"]/label/textarea')))
#     search_bar.send_keys(f'extract the information in bullet form {cleaned_text}')
#     time.sleep(5)
# except TimeoutException:
#     driver.refresh()

# # Click the send button
# send_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="component-13"]')))
# send_button.click()

# time.sleep(40)

# # Extract the response paragraph
# data_paragraph = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="chatbot"]/div[2]/div/div[2]')))
# time.sleep(3)

# # Parse the HTML content
# soup = BeautifulSoup(data_paragraph.get_attribute("innerHTML"), "html.parser")
# text = soup.get_text()
# lines = text.split('\n')

# if not text.strip():
#     print("No text found, refreshing the page")
#     driver.refresh()

# # Parsing lines into a dictionary
# data = {}
# for line in lines:
#     if ": " in line:
#         key, value = line.split(": ", 1)
#         data[key] = value
#     else:
#         print(f"Skipping line: {line}")

# # Converting dictionary into a DataFrame
# df = pd.DataFrame([data])

# if summrydata:
#     df['Target Results'] = summrydata
# else:
#     # Add a 'Target Results' column with value 'Not Detected'
#     df['Target Results'] = 'Not Detected'


# # Write DataFrame to CSV
# df.to_csv('output.csv', index=False)

# # Printing the DataFrame
# print(df)
