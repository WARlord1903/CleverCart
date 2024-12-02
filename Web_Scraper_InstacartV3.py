from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from databaseupdated import cache_item
from time import sleep

def search_items(keyword, store):
    # List of stores to search
    stores = ["publix", "food-city", "kroger", "sams-club", "food-lion", "aldi"]

    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)

    all_items = []

    driver.get(f'https://www.instacart.com/store/{stores[store]}/s?k={keyword}')
    
    scroll_pause_time = 5
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll incrementally
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(scroll_pause_time)

        # Check if new content loaded by comparing scroll heights
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    try:
        # Extract product names and full prices
        product_names = driver.find_elements(By.CSS_SELECTOR, 'h2.e-147kl2c')  # Update this selector for product names
        price_elements = driver.find_elements(By.CSS_SELECTOR, 'span.e-1ip314g')  # Replace with the selector for full price

        for i in range(len(product_names)):
            try:
                item_name = product_names[i].get_attribute('innerText').strip()

                # Check if the keyword is in the product name
                if keyword.lower() in item_name.lower():
                    # Try to get the price for the item
                    raw_price = price_elements[i].get_attribute('innerText').strip()

                    # Handle cases with "per" unit indicators or estimated prices
                    if any(unit in raw_price.lower() for unit in ["/pkg", "(est..)", "each", "per lb"]):
                        # Format variable or estimated price with indication
                        full_price_formatted = f"{raw_price} (estimated)"
                    else:
                        # Process as a standard price (assume last two digits are cents)
                        raw_price = raw_price.replace("$", "")
                        if len(raw_price) > 2:
                            price_dollars = raw_price[:-2]
                            price_cents = raw_price[-2:]
                        else:
                            price_dollars = raw_price
                            price_cents = "00"

                        # Format the price as "$dollars.cents"
                        full_price_formatted = f"${price_dollars}.{price_cents}"

                    # Add the item to the list with formatted price and store name
                    all_items.append((item_name, full_price_formatted, store))

            except (IndexError, NoSuchElementException):
                print(f"Missing data for item at index {i}. Skipping...")

    except StaleElementReferenceException:
        print("Stale elements detected. Retrying...")


    driver.quit()

    for item in all_items:
        cache_item(keyword, item[0], item[1], stores[store])

    # Print results directly
    # if all_items:
    #     for item_name, item_price, store_name in all_items:
    #         print(f"Item: {item_name}, Price: {item_price}, Store: {store_name}")
    # else:
    #     print(f"No items found for '{keyword}'.")

    return all_items

# Example usage with a keyword
#search_items("banana")
