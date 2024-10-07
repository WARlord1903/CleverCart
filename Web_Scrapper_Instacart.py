import requests
from bs4 import BeautifulSoup

# Define the URL of the Instacart page you want to scrape
url = 'https://www.instacart.com/store/publix/storefront'

# Send a request to fetch the HTML content
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the relevant section for ingredients (modify based on actual HTML structure)
    ingredients = soup.find_all('div', class_='item-container')  # Change this to the actual class name

    # List to store the scraped ingredient data
    ingredient_data = []

    # Loop through the ingredients and extract relevant information
    for item in ingredients:
        name = item.find('span', class_='item-name').text.strip()  # Change this based on actual structure
        price = item.find('span', class_='item-price').text.strip()  # Change this based on actual structure
        
        # Append the data to the list
        ingredient_data.append({
            'name': name,
            'price': price
        })

    # Print the scraped data
    for ingredient in ingredient_data:
        print(f"Ingredient: {ingredient['name']}, Price: {ingredient['price']}")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
