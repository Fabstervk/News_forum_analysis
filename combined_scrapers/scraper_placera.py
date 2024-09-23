import os
import csv
import time
import multiprocessing
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# Global variables for CSV file handling
csv_filename = "combined_output.csv"
csv_headers = ["Thread Title", "Post number", "Post Date", "Post Content"]

def scroll_to_load_all_threads(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust sleep time if necessary
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scraper_three(lock):
    chrome_driver_path = '/workspaces/News_forum_analysis/downloads/chromedriver-linux64/chromedriver'
    chrome_binary_path = '/workspaces/News_forum_analysis/downloads/chrome-linux64/chrome'

    # Check if paths exist
    if not os.path.exists(chrome_driver_path):
        print(f"ChromeDriver not found at {chrome_driver_path}")
        return

    if not os.path.exists(chrome_binary_path):
        print(f"Chrome binary not found at {chrome_binary_path}")
        return

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.binary_location = chrome_binary_path
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")

    # Set up the service with ChromeDriver
    service = Service(executable_path=chrome_driver_path)

    # Initialize WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the forum page
        forum_url = "https://forum.placera.se/upptack/populart"
        driver.get(forum_url)
        print(f"Navigated to forum page: {forum_url}")

        # Wait for the page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "text-surface-strong"))
        )
        print("Forum page loaded successfully.")

        # Scroll to load all threads
        scroll_to_load_all_threads(driver)

        # Extract thread elements
        thread_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'text-surface-strong')]")
        print(f"Found {len(thread_elements)} valid threads.")

        # Loop through each thread
        for i in range(len(thread_elements)):
            try:
                # Re-fetch the thread elements in case of stale references
                thread_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'text-surface-strong')]")
                thread = thread_elements[i]

                thread_title = thread.text.strip()
                thread_url = thread.get_attribute("href")
                print(f"\nScraping thread: {thread_title}")

                # Click the thread link to navigate to the post content
                driver.get(thread_url)

                # Wait for the post content to load
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "post-body"))
                )
                print(f"Post page loaded successfully: {thread_url}")

                # Extract the post content and date using the correct classes
                post_elements = driver.find_elements(By.CLASS_NAME, "post-body")
                date_elements = driver.find_elements(By.CLASS_NAME, "text-regular-m")

                for post, date in zip(post_elements, date_elements):
                    post_content = post.text.strip()
                    post_date = date.text.strip()
                    with lock:  # Ensure thread safety when writing to CSV
                        with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
                            csv_writer = csv.writer(csvfile)
                            csv_writer.writerow([thread_title, post_date, post_content])  # Write to CSV
                            print(f"Written Post of thread {thread_title} to CSV.")

                # Go back to the forum page
                driver.back()
                time.sleep(1)  # Wait for the page to load before the next iteration

            except StaleElementReferenceException:
                print("StaleElementReferenceException caught. Re-fetching thread elements.")
                continue  # Re-attempt the current iteration if stale reference occurs

        print("Finished scraping all threads.")

    finally:
        driver.quit()
        print("WebDriver closed.")

if __name__ == '__main__':
    lock = multiprocessing.Lock()

    # Create the CSV file and write headers if it doesn't exist
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(csv_headers)

    # Start the scraper process
    p = multiprocessing.Process(target=scraper_three, args=(lock,))
    p.start()
    p.join()  # Wait for the scraper to finish
