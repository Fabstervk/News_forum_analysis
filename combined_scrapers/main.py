import os
import csv
import multiprocessing
from scraper_borssnack import scraper_one
from scraper_flashback import scraper_two
from scraper_placera import scraper_three

if __name__ == '__main__':
    lock = multiprocessing.Lock()
    
    # Create the CSV file and write headers if it doesn't exist
    csv_filename = "combined_output.csv"
    csv_headers = ["Thread Title", "Post Date", "Post Content"]

    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(csv_headers)

    # Start the scraper processes
    p1 = multiprocessing.Process(target=scraper_one, args=(lock,))
    p2 = multiprocessing.Process(target=scraper_two, args=(lock,))
    p3 = multiprocessing.Process(target=scraper_three, args=(lock,))

    processes = [p1, p2, p3]
    
    for p in processes:
        p.start()

    # Wait for all processes to complete
    for p in processes:
        p.join()

    print("All scrapers have finished.")
