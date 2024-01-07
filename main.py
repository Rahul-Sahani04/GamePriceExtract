import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions

from currency_converter import CurrencyConverter

currency_conv = CurrencyConverter()

# Set up ChromeOptions for headless browsing
chrome_options = ChromeOptions()
chrome_options.headless = False

chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-running-insecure-content")

# Initialize the WebDriver with ChromeOptions
driver = Chrome(options=chrome_options)

# Read the game list from the CSV file
game_list = []
with open("game_list.csv", "r") as csvfile:
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

# Iterate through the list of games and websites
for game in game_list:
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
    index = 0
    for game in game_prices:
        if game[0] == "₹":
            print(currency_conv.convert(game[1:], "INR", "EUR"))
            game_prices[index] = "€" + round(
                str(currency_conv.convert(game[1:], "INR", "EUR")), 2
            )
        elif game[0] == "$":
            print(currency_conv.convert(game[1:], "USD", "EUR"))
            game_prices[index] = "€" + round(
                str(currency_conv.convert(game[1:], "USD", "EUR")), 2
            )
        # elif game[0] == "₹":
        #     pass
        # elif game[0] == "":
        #     pass
        else:
            pass
        index += 1

    print("NEW:", game_prices)

    data.append(
        [
            game_id,
            game_name,
            game_prices[0],
            game_prices[1],
            game_prices[2],
            game_prices[3],
        ]
    )

# Save the extracted data to the CSV file
with open(csv_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Write the header
    writer.writerow(header)

    # Write the data
    writer.writerows(data)

# Close the WebDriver
driver.quit()

print(f"Data saved to {csv_file}")
