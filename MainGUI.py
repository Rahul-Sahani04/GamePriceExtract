import csv
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions
import threading
from queue import Queue


# Function to process CSV and scrape game prices in a separate thread
def process_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        game_list = []

        # Read the selected CSV file
        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                game_list.append(row)

        # Create a CSV file for storing the data
        csv_file = "game_prices.csv"

        # Create a CSV header
        header = ["Product ID", "Name", "KingUIN", "Gamivo", "Eneba", "G2A"]

        # List of dictionaries with website names and their specific locators
        websites = [
            {
                "name": "kinguin",
                "url": "https://www.kinguin.net/listing?active=1&hideUnavailable=0&phrase=",
                "locator": (By.XPATH, "//span[@itemprop='lowPrice']"),
            },
            {
                "name": "gamivo",
                "url": "https://www.gamivo.com/search/",
                "locator": (
                    By.XPATH,
                    "//span[@data-testid='product-tile__product--min-price']",
                ),
            },
            {
                "name": "eneba",
                "url": "https://www.eneba.com/store/all?text=",
                "locator": (By.CSS_SELECTOR, "span.L5ErLT"),
            },
            {
                "name": "g2a",
                "url": "https://www.g2a.com/search?query=",
                "locator": (By.XPATH, "//span[@data-locator='zth-price']"),
            },
        ]

        # Initialize an empty list to store the extracted data
        data = []
        total_games = len(game_list)
        progress = 0
        progress_queue = Queue()

        # Function to scrape prices for a game
        def scrape_game(game, driver, queue):
            nonlocal progress
            game_name = game["Name"]
            game_id = game["Product ID"]

            game_prices = []

            for website in websites:
                # Navigate to the URL
                driver.get(website["url"] + game_name)

                try:
                    # Wait for the price element to be present
                    price_element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located(website["locator"])
                    )

                    # Extract the price
                    price = price_element.text
                    print(price_element.text)

                except:
                    price = "Price not found"

                game_prices.append(f"{price}")

            data.append([game_id, game_name, ", ".join(game_prices)])
            progress += 1
            queue.put(progress)
            print("DATA: ", data)

        # Function to update the progress bar
        def update_progress():
            global progress
            while progress < total_games:
                progress = progress_queue.get()
                progress_bar["value"] = (progress / total_games) * 100
                root.update_idletasks()

        # Create a ChromeOptions object for this thread
        chrome_options = ChromeOptions()
        chrome_options.headless = False
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        driver = Chrome(options=chrome_options)

        # Start a thread to update the progress bar
        progress_thread = threading.Thread(target=update_progress)
        progress_thread.start()

        # Start scraping the games
        for game in game_list:
            scrape_thread = threading.Thread(
                target=scrape_game, args=(game, driver, progress_queue)
            )
            scrape_thread.start()

        # Wait for all scraping threads to finish
        for thread in threading.enumerate():
            if thread != progress_thread:
                thread.join()

        # Close the WebDriver
        driver.quit()

        # Save the extracted data to the CSV file
        with open(csv_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Write the header
            writer.writerow(header)

            # Write the data
            print("Write ", data, "\n\n")
            writer.writerows(data)

        # Update the status label
        status_label.config(text=f"Data saved to {csv_file}")


# Create the main GUI window
root = tk.Tk()
root.geometry("400x200")
root.title("Game Price Scraper")


# Create and configure a button to select a CSV file
select_file_button = tk.Button(root, text="Select CSV File", command=process_csv)
select_file_button.pack(pady=10, padx=50)

# Create a label to display the status or results
status_label = tk.Label(root, text="")
status_label.pack(pady=5, padx=20)

# Create a progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress_bar.pack(padx=20, pady=10)

root.mainloop()
