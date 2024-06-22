import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Define the URL
url = 'https://www.arrabalesmotor.com/coches/todos-tipos/madrid/?page=1'

# Custom headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to fetch the webpage content with retries
def fetch_webpage(url, headers, retries=5, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check if the request was successful
            return response
        except requests.exceptions.RequestException as e:
            print(f'Attempt {attempt + 1} failed: {e}')
            if attempt < retries - 1:
                print(f'Retrying in {delay} seconds...')
                time.sleep(delay)
            else:
                print('All attempts failed.')
                raise

# Try to fetch the webpage content
try:
    response = fetch_webpage(url, headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the container that holds the vehicle information
    vehicles = soup.find_all('div', class_='card card--boxed card--theme-light card--spacing-none vcard vcard--classic vcard--border-default vcard--shadow-none vcard--status-free vcard--layout-block')
    print("Num. Cars: " + str(len(vehicles)))

    # Create a list to store vehicle details
    vehicle_data = []

    # Loop through each vehicle container and extract details
    for vehicle in vehicles:
        # print("CAR: " + str(vehicle))
        try:
            title = vehicle.find('div', class_='vcard-main-info__make-model ws-skeleton').text.strip()
            print("Titulo: " + str(title))
            
            version = vehicle.find('div', class_='vcard-main-info__version ws-skeleton').text.strip()
            print("Version: " + str(version))
            
            price_initial = vehicle.find('p', class_='vcard-price__initial--price large').text.strip()
            print("Precio inicial: " + str(price_initial))

            discount = vehicle.find('span', class_='ebadge__text').text.strip()
            print("Dto: " + str(discount))
            
            price_final = vehicle.find('div', class_='vcard-price__price bold').text.strip()
            print("Precio final: " + str(price_final))

            fuel_info = vehicle.find('p', class_='vcard-consumption__title').text.strip()
            print("Fuel: " + str(fuel_info))
            car_date, car_kms, car_fuel = fuel_info.split('-')
            print("Car Date: " + car_date)
            print("Car Kms: " + car_kms)
            print("Car Fuel: " + car_fuel)

            consumption = vehicle.find('span', class_='text text__default text__color--inherit text__font--primary').text.strip()
            print("Consumo: " + consumption)

            # co2_class = vehicle.find('span', text=lambda x: 'Clase de CO2' in x).text.strip()
            # image_url = vehicle.find('picture', class_='image media--ratio-4/3 vcard-header__element vcard-header__image').find('img')['src']
            # link = vehicle.find('a', class_='vcard--link')['href']
            
            # Add data to the list
            vehicle_data.append({
                 'Modelo': title,
                 'Version': version,
                 'Precio Inicial': price_initial,
                 'Descuento': discount,
                 'Precio Final': price_final,
                 'Fecha Matriculacion': car_date.strip(),
                 'Kilometros': car_kms.strip(),
                 'Tipo Motor': car_fuel.strip(),
                 'Consumo': consumption,
            #     'CO2 Class': co2_class,
            #     'Image URL': image_url,
            #     'Link': link
            })
        except AttributeError as e:
            # Skip if any expected detail is not found
            print(e)
            continue

    # Convert the list to a DataFrame
    df = pd.DataFrame(vehicle_data)

    # print(df)

    # Save the DataFrame to a CSV file
    df.to_csv('used_vehicles.csv', index=False)

    print('Data has been scraped and saved to used_vehicles.csv')

except Exception as e:
    print(f'Failed to retrieve data: {e}')
