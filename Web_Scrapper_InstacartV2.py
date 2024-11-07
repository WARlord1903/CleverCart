from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from time import sleep

def search_items(item):
    # Initialize Chrome WebDriver with options
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    driver = webdriver.Chrome(options=chrome_options)  # Start Chrome instance

    driver.get('https://www.instacart.com/store/publix/s?k=' + item)  # Search for the item on Instacart

    # Increase wait time
    wait = WebDriverWait(driver, 20)

    # Keep track of found items
    found_items = 0
    prev_found_items = 0

    # Search items until the page is fully updated
    while prev_found_items != found_items or found_items == 0:
        try:
            # Refetch product names and prices each time to avoid stale references
            ingredients = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'h2.e-147kl2c')))  # Adjust this selector
            price_elements_dollars = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.e-1qkvt8e')))  # Adjust based on actual class for dollar part
            price_elements_cents = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.e-p745l')))  # Adjust based on actual class for cent part

            # Extract product names
            ingredient_text = [i.text for i in ingredients if i.text.strip() != ""]
            
            # Extract and combine prices (dollars and cents), handling missing values
            prices = []
            for dollars, cents in zip(price_elements_dollars, price_elements_cents):
                dollar_value = dollars.text.strip() if dollars.text.strip() else "0"
                cent_value = cents.text.strip() if cents.text.strip() else "00"

                # If either dollars or cents is missing, handle properly
                if cent_value == "00":
                    full_price = f"{dollar_value}"
                else:
                    full_price = f"{dollar_value}.{cent_value}"

                prices.append(full_price)

            # Combine names and prices
            items_with_prices = list(zip(ingredient_text, prices))

            # Update the found item count
            prev_found_items = found_items
            found_items = len(ingredients)
            sleep(3)

        except StaleElementReferenceException:
            # In case of stale element reference, refetch the elements and retry
            print("StaleElementReferenceException caught. Refetching elements...")

    driver.quit()  # Stop Chrome instance

    # Return the list of ingredients and prices
    return items_with_prices

# # Example usage
# lays_list = search_items("avocado")

# # Print the returned items with prices
# for item_name, item_price in lays_list:
#     print(f"Item: {item_name}, Price: {item_price}")
