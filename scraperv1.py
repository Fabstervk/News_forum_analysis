import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Path to ChromeDriver and Chrome binary
chrome_driver_path = 'chromedriver-linux64/chromedriver'
chrome_binary_path = '/workspaces/News_forum_analysis/uploaded_files/chrome-linux64/chrome'

# Check if paths exist
if not os.path.exists(chrome_driver_path):
    print(f"ChromeDriver not found at {chrome_driver_path}")
else:
    print(f"ChromeDriver found at {chrome_driver_path}")

if not os.path.exists(chrome_binary_path):
    print(f"Chrome binary not found at {chrome_binary_path}")
else:
    print(f"Chrome binary found at {chrome_binary_path}")

# Set up Chrome options to specify the custom binary location and run in headless mode
chrome_options = Options()
chrome_options.binary_location = chrome_binary_path
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")

# Set up the service with ChromeDriver
service = Service(executable_path=chrome_driver_path)

# Initialize WebDriver with the custom Chrome binary
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Step 1: Navigate to the Flashback forum page (first page)
    forum_url = "https://www.flashback.org/f487"
    driver.get(forum_url)
    print(f"Navigated to {forum_url}")
    
    # Add an explicit wait for the page to load completely
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "td.td_title"))
    )
    print("Page loaded successfully.")
    
    # Step 2: Extract page source and inspect the structure
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    
    # Step 3: Find the correct thread links
    thread_links = []
    threads = soup.find_all("td", class_="td_title")  # Finding all threads
    
    for thread in threads:
        # Find the thread link inside the td.td_title
        link = thread.find("a", href=True)
        if link:
            full_link = f"https://www.flashback.org{link['href']}"
            thread_links.append(full_link)
    
    print(f"Found {len(thread_links)} thread links.")

    # Step 4: Optionally visit each thread
    for thread_link in thread_links:
        print(f"Scraping thread: {thread_link}")
        driver.get(thread_link)
        time.sleep(2)  # Wait for the page to load

        # Parse the page content with BeautifulSoup
        thread_soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Extract the conversation posts
        posts = thread_soup.find_all("div", class_="post_message")
        for idx, post in enumerate(posts):
            message = post.get_text(strip=True)
            print(f"Post {idx + 1}: {message}")
            print("="*80)

        # Navigate back to the forum page after scraping the thread
        driver.back()
        time.sleep(2)

    # Close the browser
    driver.quit()

except Exception as e:
    print(f"An error occurred: {e}")
    driver.quit()
