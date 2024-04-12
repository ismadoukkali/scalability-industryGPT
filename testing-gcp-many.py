import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor

# Replace with your Google Cloud Function's URL
url_internal = "https://europe-southwest1-industry-gpt-scalability.cloudfunctions.net/industry-gpt"
url_external = "https://europe-southwest1-scalabilitygpt.cloudfunctions.net/industrygpt-scalability-v1"
local = "http://localhost:8080"

# Replace with your actual API key
api_key = "APOLO-API-KEY"

# Parameters to be sent to the cloud function
data_1 = {
    "name": "Scalability",
    "url": "https://www.g2.com/categories",
    "company_id": "123456789",
    "employee_count": 50,
    "founded_date": 2018,
    "linkedin_industry": "Marketing & Advertising",
    "founding_data": "",
    "extra_descriptors": ""
}

data_2 = {
    "name": "Apolo",
    "url": "https://www.apolomarketing.net",
    "company_id": "123456789",
    "employee_count": 50,
    "founded_date": 2018,
    "linkedin_industry": "Marketing & Advertising",
    "founding_data": "",
    "extra_descriptors": ""
}

data_3 = {
    "name": "Upflow",
    "url": "https://upflow.io",
    "company_id": "123456789",
    "employee_count": 50,
    "founded_date": 2018,
    "linkedin_industry": "Financial Services",
    "founding_data": "",
    "extra_descriptors": ""
}

data_4 = {
    "name": "Qonto",
    "url": "https://www.getscalability.io",
    "company_id": "123456789",
    "employee_count": 700,
    "founded_date": 2018,
    "linkedin_industry": "Marketing & Advertising",
    "founding_data": "",
    "extra_descriptors": ""
}

data_5 = {
    "name": "MangoPay",
    "url": "https://mangopay.com/",
    "company_id": "123456789",
    "employee_count": 500,
    "founded_date": 2018,
    "linkedin_industry": "Marketing & Advertising",
    "founding_data": "",
    "extra_descriptors": ""
}

# Headers including the API key
headers = {
    "Content-Type": "application/json",
    "APOLO-API-KEY": api_key
}

datas = [data_1]
executor = ThreadPoolExecutor(10)
futures = []

def make_request(url_external, headers, data):
    response = requests.post(url_external, headers=headers, data=json.dumps(data))
    # Checking the response
    if response.status_code == 200:
        # Parse the response as JSON (which converts it to a Python dictionary)
        response_data = response.json()

        # Pretty-printing the Python dictionary
        #pretty_json = json.dumps(response_data, indent=4)
        return "Success:", response_data
    else:
        return "Error:", response.text
    
for data in datas:
    # Making a POST request
    future = executor.submit(make_request, url_external, headers, data)
    futures.append(future)

for future in futures:
    print('')
    print(future.result())

    


