import os
import multiprocessing
from scraper_borssnack import scraper_one  # Import the scraper directly

if __name__ == '__main__':
    lock = multiprocessing.Lock()

    # Start the scraper process
    p = multiprocessing.Process(target=scraper_one, args=(lock,))
    p.start()
    p.join()  # Wait for the scraper to finish
