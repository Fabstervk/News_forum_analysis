import os
import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import multiprocessing

# Global variables for CSV file handling
csv_filename = "combined_output.csv"
csv_headers = ["Index", "Thread Title", "Post Date", "Post Content", "Static URL"]

def scraper_two(lock):
    # Path to ChromeDriver and Chrome binary
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

    # Write the header row if file is empty
    with lock:
        if not os.path.exists(csv_filename) or os.path.getsize(csv_filename) == 0:
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(csv_headers)

    # Initialize WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the forum page
        forum_url = "https://www.flashback.org/f487"  # Forum section URL
        driver.get(forum_url)
        print(f"Navigated to forum page: {forum_url}")

        # Wait for the page to load and find thread links using XPath
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[starts-with(@id, 'thread_title_')]"))
        )
        print("Forum page loaded successfully.")

        # Extract thread links and titles using XPath
        thread_elements = driver.find_elements(By.XPATH, "//a[starts-with(@id, 'thread_title_')]")

        thread_links = []
        thread_titles = []  # Store thread titles

        for thread in thread_elements:
            thread_links.append(thread.get_attribute("href"))  # Extract the href (URL)
            thread_titles.append(thread.text.strip())  # Extract the thread title

        print(f"Found {len(thread_links)} valid threads.")

        # Loop through each thread and scrape posts from the last page
        for thread_index, (thread_url, thread_title) in enumerate(zip(thread_links, thread_titles), start=1):
            print(f"\nScraping thread {thread_index}/{len(thread_links)}: {thread_url}")
            driver.get(thread_url)

            # Wait for the thread page to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.post_message"))
                )
                print(f"Thread page loaded successfully: {thread_url}")
            except TimeoutException:
                print(f"Timeout while waiting for the thread page to load: {thread_url}. Skipping this thread.")
                continue  # Skip to the next thread if there's a timeout

            # Find the span element with "Sidan X av Y" to get the last page number
            try:
                last_page_span = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[contains(@class, 'select2-selection__placeholder')]")
                    )
                )
                last_page_text = last_page_span.get_attribute("innerText")
                print(f"Found page info: {last_page_text}")

                # Extract the last page number using regex
                match = re.search(r'Sidan \d+ av (\d+)', last_page_text)
                if match:
                    last_page_number = match.group(1)
                    print(f"Last page number for {thread_url}: {last_page_number}")
                else:
                    print(f"Could not find last page number for {thread_url}. Assuming 1.")
                    last_page_number = 1  # Default to 1 if not found

            except Exception as e:
                print(f"Could not find last page number span for thread {thread_url}: {e}")
                last_page_number = 1  # Default to 1 if there's an error
                print(f"Assuming last page number is 1 for {thread_url}.")

            # Construct the last page URL dynamically
            last_page_url = f"{thread_url}p{last_page_number}"
            print(f"Constructed last page URL: {last_page_url}")

            # Navigate to the last page URL
            try:
                driver.get(last_page_url)
                print(f"Navigated to last page: {last_page_url}")
            except Exception as e:
                print(f"Error navigating to last page URL: {last_page_url}. Error: {e}")
                continue  # Skip to the next thread if there's a navigation error

            # Wait for the last page to load
            try:
                WebDriverWait(driver, 20).until(  # Increased wait time to 20 seconds
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.post_message"))
                )
                print("Last page loaded successfully.")
            except TimeoutException:
                print(f"Timeout while waiting for the last page to load: {last_page_url}. Skipping this thread.")
                continue  # Skip to the next thread if there's a timeout

            # Extract page source of the last page
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Scrape the content of all posts on the last page
            posts = soup.find_all("div", class_="post_message")
            post_dates = soup.find_all("div", class_="post-heading")  # Assuming this class holds the post date

            print(f"Found {len(posts)} posts on the last page of thread {thread_url}.")

            # Write each post to the CSV file
            for index, (post, date) in enumerate(zip(posts, post_dates), start=1):
                post_content = post.get_text(separator='\n', strip=True)
                post_date = date.get_text(strip=True)  # Extract date
                static_url = "https://www.flashback.org/f487"

                with lock:  # Ensure thread safety when writing to CSV
                    with open("combined_output.csv", mode='a', newline='', encoding='utf-8') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow([index, thread_title, post_date, post_content, static_url])  # Each post has its own row
                print(f"Written Post {index} of thread {thread_url} to CSV.")

            # Pause between requests to avoid overwhelming the server
            time.sleep(1)  # 1 second pause

        print("Finished scraping all threads.")

    finally:
        driver.quit()
        print("WebDriver closed.")

