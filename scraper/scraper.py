import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import os

# Custom headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

baseURL = 'https://www.arrabalesmotor.com/coches/todos-tipos/madrid/?page=1' # Define the base URL
firstURL = 'https://www.arrabalesmotor.com/coches/todos-tipos/madrid/' # Define the base URL
pageNo = 1 # Page number
curURL = baseURL # Current URL
morePages = True # web pagination
carNo = 0 # Vehicle number

# Create a list to store vehicle details
vehicle_data = []

NO_INFO = "Sin información" # default str data value


'''
Function to increment the page number of a URL
'''
def increment_page_number(url: str) -> str:
    # Parse the URL into its components
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Get the current page number and increment it
    current_page = int(query_params.get('page', [1])[0])
    new_page = current_page + 1
    
    # Update the query parameters with the new page number
    query_params['page'] = [str(new_page)]
    
    # Reconstruct the URL with the updated query parameters
    new_query_string = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query_string))
    
    return new_url

'''
Funciton to Get file name from URL
'''
def get_filename_from_url(url: str) -> str:
    # Parse the URL to get the path
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # Extract the file name
    filename_with_extension = os.path.basename(path)
    
    # Remove the file extension
    filename_without_extension = os.path.splitext(filename_with_extension)[0]
    
    # Replace dashes with spaces
    filename_with_spaces = filename_without_extension.replace('-', ' ')
    
    return filename_with_spaces



''' 
Function to fetch the webpage content with retries
'''
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

# Fetch site content
while morePages:
    try:
        if pageNo < 2:
            response = fetch_webpage(firstURL, headers, retries=1)
        else:
            response = fetch_webpage(curURL, headers, retries=1)
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the container that holds the vehicle information
        vehicles = soup.find_all('div', class_='card card--boxed card--theme-light card--spacing-none vcard vcard--classic vcard--border-default vcard--shadow-none vcard--status-free vcard--layout-block')
        print("Num. Cars: " + str(len(vehicles)))

        # Loop through each vehicle container and extract details
        for vehicle in vehicles:

            # Initialize car data
            carNo += 1
            carId = str(carNo)
            print(f'CAR {carId}') # {str(vehicle)}')
            title = NO_INFO
            version = NO_INFO
            price_initial = NO_INFO
            discount = NO_INFO
            price_final = NO_INFO
            car_date = NO_INFO
            car_kms = NO_INFO
            car_fuel = NO_INFO
            consumption = NO_INFO
            env_label = NO_INFO
            image_url = ""
            link = ""

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
                # car_date, car_kms, car_fuel = fuel_info.split('-')
                fuel_info_list = fuel_info.split('-')
                if len(fuel_info_list) < 1:
                    car_date = ""
                    car_kms = ""
                    car_fuel = ""
                elif len(fuel_info_list) == 1:
                    car_date = fuel_info_list[0]
                    car_kms = ""
                    car_fuel = ""
                elif len(fuel_info_list) == 2:
                    car_date = fuel_info_list[0]
                    car_kms = fuel_info_list[1]
                    car_fuel = ""
                else:
                    car_date = fuel_info_list[0]
                    car_kms = fuel_info_list[1]
                    car_fuel = fuel_info_list[2]

                print("Car Date: " + car_date)
                print("Car Kms: " + car_kms)
                print("Car Fuel: " + car_fuel)

                consumption = vehicle.find('span', class_='text text__default text__color--inherit text__font--primary').text.strip()
                print("Consumo: " + consumption)

                if vehicle.find('picture', class_='image media--ratio-unset environmental-icon') is not None:
                    env_label_pic = vehicle.find('picture', class_='image media--ratio-unset environmental-icon').find('img')['src']
                    env_label = get_filename_from_url(env_label_pic)
                    print("Etiqueta: " + env_label)
                else:
                    env_label = NO_INFO


                image_url = vehicle.find('picture', class_='image media--ratio-4/3 vcard-header__element vcard-header__image ws-skeleton').find('img')['src']
                print("Image: " + image_url)

                if vehicle.find('a', class_='vcard--link') is not None:
                    link = vehicle.find('a', class_='vcard--link')['href']
                else:
                    link = vehicle.find('a', class_='vcard-main-info__make-model ws-skeleton')['href']
            
                # link = vehicle.find('a', class_='vcard--link')['href']
                # link = vehicle.find('a', class_='vcard-main-info__make-model ws-skeleton')['href']
                print(link)
            
                # Add data to the list
                vehicle_data.append({
                    'ID': carId,
                    'Modelo': title,
                    'Version': version,
                    'Precio Inicial': price_initial,
                    'Descuento': discount,
                    'Precio Final': price_final,
                    'Fecha Matriculacion': car_date.strip(),
                    'Kilometros': car_kms.strip(),
                    'Tipo Motor': car_fuel.strip(),
                    'Consumo': consumption,
                    'Etiqueta Ambiental': env_label, 
                    'URL imagen': image_url,
                    'Enlace': link
                })
            except AttributeError as e:
                # Skip if any expected detail is not found
                print(f'Error retrieving data for car {carId}: {e}')
                # Add data to the list anyway
                vehicle_data.append({
                    'ID': carId,
                    'Modelo': title,
                    'Version': version,
                    'Precio Inicial': price_initial,
                    'Descuento': discount,
                    'Precio Final': price_final,
                    'Fecha Matriculacion': car_date.strip(),
                    'Kilometros': car_kms.strip(),
                    'Tipo Motor': car_fuel.strip(),
                    'Consumo': consumption,
                    'Etiqueta Ambiental': env_label, 
                    'URL imagen': image_url,
                    'Enlace': link
                })
                continue

        # Go to next page
        curURL = increment_page_number(curURL)
        pageNo += 1

    except Exception as e:
        print(f'Failed to retrieve data in page {pageNo}: {e}')
        morePages = False

# Done crawling
# Convert the list to a DataFrame
df = pd.DataFrame(vehicle_data)
# print(df)

# Save the DataFrame to a CSV file
df.to_csv('used_vehicles.csv', index=False)

# Save DataFrame to JSON file
df.to_json('used_vehicles.json', orient='records', lines=True, force_ascii=False)

print('Data has been scraped and saved to used_vehicles.csv')