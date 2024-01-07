import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import csv
import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions
from currency_converter import CurrencyConverter

from concurrent.futures import ThreadPoolExecutor

currency_conv = CurrencyConverter()

# Set up ChromeOptions for headless browsing
chrome_options = ChromeOptions()
chrome_options.headless = False

chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--disable-renderer-backgrounding")
chrome_options.add_argument("--disable-backgrounding-occluded-windows")

# Create a CSV file for storing the data
csv_file = "game_prices.csv"

# Create a CSV header
header = ["Product ID", "Name", "KingUIN", "Gamivo", "Eneba", "G2A"]

# List of dictionaries with website names and their specific locators
websites = [
    {
        "name": "kinguin",
        "url": "https://www.kinguin.net/listing?active=1&hideUnavailable=0&phrase=",
        "locator": (By.XPATH, "//*[@id='c-page__content']/div/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div/div[3]/div[2]/span[4]"),
    },
    {
        "name": "gamivo",
        "url": "https://www.gamivo.com/search/",
        "locator": (
            By.XPATH,
            "/html/body/app-root/div/div/app-search-serp/div/app-search-results/section/div/div[2]/div[2]/app-product-tile[1]/div/div[2]/div[2]/p[1]/span",
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

# Function to scrape game prices for a single website
def scrape_game_prices(game, column_name, driver, website):
    game_name = game[column_name]
    game_id = game["Product ID"]
    game_prices = {}

    # for website in websites:
    driver.get(website["url"] + game_name)

    try:
        price_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(website["locator"])
        )
        price = price_element.text
    except:
        price = "Price not found"

    # Convert the price to Euro (€)
    if price and price[0] == "₹":
        converted_price = currency_conv.convert(price[1:], "INR", "EUR")
        price = f"€{converted_price:.2f}"
    elif price and price[0] == "$":
        converted_price = currency_conv.convert(price[1:], "USD", "EUR")
        price = f"€{converted_price:.2f}"

    game_prices[website["name"]] = price

    return game_id, game_name, game_prices



# Function to start scraping process
def start_scraping():
    csv_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

    # Initialize the WebDriver with ChromeOptions
    driver = Chrome(options=chrome_options)
    driver.set_window_size(600,400)

    column_name = column_entry.get()

    # Read the game list from the CSV file
    game_list = []
    with open(csv_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            game_list.append(row)

    # Configure progress bar
    progress["maximum"] = len(game_list)

    # Disable the start button during scraping
    scrape_button.config(state=tk.DISABLED)

    # Start a thread for scraping to avoid freezing the GUI
    t = threading.Thread(
        target=process_game_list, args=(game_list, column_name, driver)
    )
    t.start()


# Function to process the game list and update progress
def process_game_list(game_list, column_name, driver):
    results = []
    with ThreadPoolExecutor() as executor:
        driver2 = Chrome(options=chrome_options)
        driver3 = Chrome(options=chrome_options)
        driver4 = Chrome(options=chrome_options)
        all_drivers = [driver, driver2, driver3, driver4]
        index = 0
        for game in game_list:
            future = executor.submit(scrape_game_prices, game, column_name, all_drivers[index])
            results.append(future)
            index += 1

    for result in results:
        game_id, game_name, game_prices = result.result()
        data.append(
            [
                game_id,
                game_name,
                game_prices["kinguin"],
                game_prices["gamivo"],
                game_prices["eneba"],
                game_prices["g2a"],
            ]
        )
        progress.step(1)

    # Save the data to CSV
    save_data_to_csv(driver)


# Function to save the extracted data to a CSV file
def save_data_to_csv(driver):
    with open(csv_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(data)
    driver.quit()
    result_label.config(text=f"Data saved to {csv_file}")
    print(f"Data saved to {csv_file}")


# Create the main window
root = tk.Tk()
root.title("Game Price Scraper")

# Add a label and entry for the column name
column_label = tk.Label(root, text="Enter the column name for game names:")
column_label.pack()
column_entry = tk.Entry(root, width=50)
column_entry.pack()

# Add a progress bar
progress = ttk.Progressbar(root, length=200, mode="determinate")
progress.pack()

# Add a button to start scraping
scrape_button = tk.Button(root, text="Start Scraping", command=start_scraping)
scrape_button.pack()

# Add a label to display the result
result_label = tk.Label(root, text="")
result_label.pack()

# Start the main event loop
root.mainloop()
