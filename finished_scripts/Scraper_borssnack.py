import os
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time

# Path to ChromeDriver and Chrome binary
chrome_driver_path = '/workspaces/News_forum_analysis/downloads/chromedriver-linux64/chromedriver'
chrome_binary_path = '/workspaces/News_forum_analysis/downloads/chrome-linux64/chrome'

# Check if paths exist
if not os.path.exists(chrome_driver_path):
    print(f"ChromeDriver not found at {chrome_driver_path}")
    exit(1)

if not os.path.exists(chrome_binary_path):
    print(f"Chrome binary not found at {chrome_binary_path}")
    exit(1)

# Set up Chrome options
chrome_options = Options()
chrome_options.binary_location = chrome_binary_path

# Enable headless mode for environments without a GUI
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("window-size=1920,1080")

# Set up the service with ChromeDriver
service = Service(executable_path=chrome_driver_path)

# Initialize WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Prepare CSV file to save the posts
csv_filename = "borssnack_forum_posts.csv"
csv_headers = ["Thread Title", "Post Number", "Post Date", "Post Content"]

with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(csv_headers)  # Write the header row

    try:
        # Navigate to the forum page
        forum_url = "https://borssnack.di.se/#/"  # Forum section URL
        driver.get(forum_url)
        print(f"Navigated to forum page: {forum_url}")

        # Wait for the page to load and find thread links
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.bn_thread__link"))
        )
        print("Forum page loaded successfully.")

        # Extract thread links
        thread_elements = driver.find_elements(By.CSS_SELECTOR, "a.bn_thread__link")

        thread_links = []  # Store thread URLs

        for thread in thread_elements:
            thread_url = thread.get_attribute("href")  # Extract the href (URL)
            print(f"Found thread URL: {thread_url}")  # Debugging print

            if thread_url:  # Check if the URL is valid
                thread_links.append(thread_url)
            else:
                print("Warning: Found thread with no URL.")

        print(f"Found {len(thread_links)} valid threads.")

        # Loop through each thread and scrape posts
        for thread_index, thread_url in enumerate(thread_links, start=1):
            print(f"\nScraping thread {thread_index}/{len(thread_links)}: {thread_url}")
            driver.get(thread_url)

            # Wait for the thread page to load and extract the thread title
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "bn_thread-body__title"))
                )
                thread_title = driver.find_element(By.CLASS_NAME, "bn_thread-body__title").text.strip()
                print(f"Thread title extracted: {thread_title}")
            except TimeoutException:
                print(f"Timeout while waiting for the thread page to load: {thread_url}. Skipping this thread.")
                continue  # Skip to the next thread if there's a timeout

            # Wait for the posts to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "bn_thread-comment__container"))
                )
                print(f"Thread page loaded successfully: {thread_url}")
            except TimeoutException:
                print(f"Timeout while waiting for posts to load: {thread_url}. Skipping this thread.")
                continue  # Skip to the next thread if there's a timeout

            # Extract the posts
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Scrape the content of all posts in the thread
            posts = soup.find_all("div", class_="bn_thread-comment__container")

            print(f"Found {len(posts)} posts in thread {thread_url}.")

            # Write each post to the CSV file
            for index, post in enumerate(posts, start=1):
                # Extract post date and content
                post_date = post.find("span", class_="bn_thread-comment__date").get_text(strip=True)
                message = post.find("div", class_="bn_thread-comment__body").get_text(separator='\n', strip=True)

                csv_writer.writerow([thread_title, index, post_date, message])  # Each post has its own row
                print(f"Written Post {index} of thread {thread_url} to CSV.")

            # Pause between requests to avoid overwhelming the server
            time.sleep(1)  # 1 second pause

        print("Finished scraping initial threads.")

        # Wait for any overlay and close it
        try:
            overlay = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "bn_help-box__overlay"))
            )
            driver.execute_script("arguments[0].click();", overlay)  # Use JavaScript to click the overlay
            print("Closed the overlay if it was present.")
        except TimeoutException:
            print("No overlay to close.")

        # Click on "Dagens trådar"
        try:
            print("Waiting for 'Dagens trådar' button to become visible...")
            button = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Dagens trådar')]"))
            )
            driver.execute_script("arguments[0].click();", button)  # Use JavaScript to click
            print("Clicked on 'Dagens trådar'.")
        except TimeoutException:
            print("Timeout while waiting for 'Dagens trådar' button. Exiting.")
            exit(1)

        # Wait for the dropdown options to become visible
        try:
            print("Waiting for dropdown options to become visible...")
            WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//ul[@class='bn_topbar-filter__list-options']"))
            )
            print("Dropdown options loaded successfully.")
        except TimeoutException:
            print("Timeout while waiting for dropdown options. Exiting.")
            exit(1)

        # Click on "Gårdagens trådar"
        try:
            print("Waiting for 'Gårdagens trådar' link to become clickable...")
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Gårdagens trådar')]"))
            ).click()
            print("Clicked on 'Gårdagens trådar'.")
        except TimeoutException:
            print("Timeout while waiting for 'Gårdagens trådar' link. Exiting.")
            exit(1)

        # Wait for the page to load and extract thread links for "Gårdagens trådar"
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.bn_thread__link"))
        )
        print("Gårdagens trådar page loaded successfully.")

        # Extract thread links for "Gårdagens trådar"
        thread_elements = driver.find_elements(By.CSS_SELECTOR, "a.bn_thread__link")
        thread_links = []  # Reset thread links for the new page

        for thread in thread_elements:
            thread_url = thread.get_attribute("href")  # Extract the href (URL)
            print(f"Found thread URL: {thread_url}")  # Debugging print

            if thread_url:  # Check if the URL is valid
                thread_links.append(thread_url)
            else:
                print("Warning: Found thread with no URL.")

        print(f"Found {len(thread_links)} valid threads in Gårdagens trådar.")

        # Loop through each thread and scrape posts for "Gårdagens trådar"
        for thread_index, thread_url in enumerate(thread_links, start=1):
            print(f"\nScraping thread {thread_index}/{len(thread_links)}: {thread_url}")
            driver.get(thread_url)

            # Wait for the thread page to load and extract the thread title
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "bn_thread-body__title"))
                )
                thread_title = driver.find_element(By.CLASS_NAME, "bn_thread-body__title").text.strip()
                print(f"Thread title extracted: {thread_title}")
            except TimeoutException:
                print(f"Timeout while waiting for the thread page to load: {thread_url}. Skipping this thread.")
                continue  # Skip to the next thread if there's a timeout

            # Wait for the posts to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "bn_thread-comment__container"))
                )
                print(f"Thread page loaded successfully: {thread_url}")
            except TimeoutException:
                print(f"Timeout while waiting for posts to load: {thread_url}. Skipping this thread.")
                continue  # Skip to the next thread if there's a timeout

            # Extract the posts
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Scrape the content of all posts in the thread
            posts = soup.find_all("div", class_="bn_thread-comment__container")

            print(f"Found {len(posts)} posts in thread {thread_url}.")

            # Write each post to the CSV file
            for index, post in enumerate(posts, start=1):
                # Extract post date and content
                post_date = post.find("span", class_="bn_thread-comment__date").get_text(strip=True)
                message = post.find("div", class_="bn_thread-comment__body").get_text(separator='\n', strip=True)

                csv_writer.writerow([thread_title, index, post_date, message])  # Each post has its own row
                print(f"Written Post {index} of thread {thread_url} to CSV.")

            # Pause between requests to avoid overwhelming the server
            time.sleep(1)  # 1 second pause

        print("Finished scraping Gårdagens trådar.")

    finally:
        driver.quit()
        print("WebDriver closed.")
