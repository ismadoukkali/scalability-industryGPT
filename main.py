import functions_framework
from openai import OpenAI
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen, Request
from dotenv import load_dotenv
import threading
from datetime import datetime
import json
import os
import requests

load_dotenv()
client = OpenAI()

def generate_response(prompt):
    response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": "You are a helpful assistant, expert in Analysing Companies."},
        {"role": "user", "content": str(prompt)},
    ],
    temperature=0
    )
    selection = response.choices[0].message.content
    return selection

def generate_response_feedback(initial_question, system_answer, feedback):
    response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": "You are a helpful assistant, expert in Analysing Companies."},
        {"role": "user", "content": str(initial_question)},
        {"role": "system", "content": str(system_answer)},
        {"role": "user", "content": str(feedback)}
    ],
    temperature=0
    )
    selection = response.choices[0].message.content
    return selection

def generate_response_gpt3(prompt):
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant, expert in Analysing Companies."},
        {"role": "user", "content": str(prompt)},
    ],
    max_tokens=300,
    temperature=0
    )
    selection = response.choices[0].message.content
    return selection

def generate_response_gpt3_json(prompt):
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": "You are a helpful assistant, expert in Analysing Companies."},
        {"role": "user", "content": str(prompt)},
    ],
    max_tokens=300,
    temperature=0
    )
    selection = response.choices[0].message.content
    return selection

def retrieve_html(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    html = urlopen(req).read()
    soup = BeautifulSoup(html, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract() 

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def selenium_search(query):
    # Replace these with your own API key and Custom Search Engine ID
    API_KEY = os.environ.get('GOOGLE_SEARCH_API')
    SEARCH_ENGINE_ID = os.environ.get('SEARCH_ENGINE_ID')

    # Base URL for Google Custom Search
    url = 'https://www.googleapis.com/customsearch/v1'

    # Parameters for the search
    params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query
    }

    # Send the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        results = response.json()
        # Return the first search result
        if 'items' in results:
            return results['items'][0]['link']
        else:
            return 'No results found'
    else:
        return f'Error: {response.status_code}'


# Client focus prompt
clients_focus = ["B2C", "B2B", "B2B/B2C"]
prompt_client_focus = """

You are given the description of a company retrieved from a company's website.

You will need to categorize the company within a Client Focus according to the taxonomy below.

There can only be ONE client focus. The answer needs to be concise and only can follow the taxonomy.

DO NOT come up with any taxonomy. STICK to the taxonomy below. 

Give your results in the format JSON  - 

'client_focus': [client focus] 


Here the taxonomy for the client focus:
B2C
B2B
B2B/B2C

"""

# Industry & Business Model Prompt
startup_industries = ["Deep Tech", "Edtech", "Fintech", "Foodtech", "Healthtech", "Insurtech", "Lawtech", "Salestech & Martech", "Mobility", "Energy", "Big data", "Cybersecurity", "Media & Telecom", "Consumer electronics", "Esports & Gaming", "Agritech", "Regtech", "Impact & diversity", "HRtech", "Cleantech", "Traveltech", "Miscellaneous", "Proptech"]
midmarket_industries = ["Finance", "Legal", "Digital", "Staffing", "Content & Marketing", "Cloud & infrastructure", "Web 3", "Data protection", "Energy", "Pharmaceutical", "Medical equipment", "Apparel", "Beauty", "Consumer goods", "Logistics & delivery", "Luxury", "FMCG", "Vehicle production", "Building & construction", "Sport", "In-store retail", "Real estate service", "Hotel & accomodation", "Restaurant and catering", "Manufacturing", "Education", "Miscellaneous", "Travel", "Agriculture"]
corporate_industries = ["Finance & Legal", "Technology", "Media & Telecommunication", "Consulting", "Insurance", "Recruitment", "Construction", "Energy & Chemical", "Automotive", "Retail", "Real estate", "Healthcare", "Travel", "Fashion", "Food & Beverage", "Education", "Logistics & Transportation", "Environmental", "Food & Beverage", "Education", "Logistics & Transportation", "Miscellaneous"]
business_models = ["SaaS", "Marketplace", "Ecommerce", "Service", "Manufacturing"]
prompt_industry_business =  f"""

You are given the description of a company retrieved from a company's website.

You will need to categorize the company within their Industry and Business Model Category according to the taxonomy below.

Only resort to a Miscellaneous industry if its really not clear, always prioritize other industries.

There can only be ONE industry and ONE business model. The answer needs to be concise and only can follow the taxonomy.

DO NOT come up with any taxonomy. STICK to the taxonomy below. 

Give your results in the format format JSON - 

'industry': [industry] 
'business_model': [business model]

Here the taxonomy for each of the Industries and Business Models - 

Business Models:
SaaS
Marketplace
Ecommerce
Service
Manufacturing 

Industries:

"""

# Ecommerce prompt
ecomm_industries = ["Food", "Apparel & Fashion", "Cosmetic & Beauty", "Miscellaneous"]

prompt_industry_business_ecomm =  f"""

You are given the description of a company retrieved from a company's website.

You will need to categorize the company within their Industry category according to the taxonomy below.

Only resort to the Miscellaneous industry if the industry is really not clear, always prioritize other industries. 

There can only be ONE industry. The answer needs to be concise and only can follow the taxonomy.

DO NOT come up with any taxonomy. STICK to the taxonomy below. 

Give your results in the format format JSON - 

'industry': [industry] 

Here the categories for each of the Industries - 

Industries:
'Food' - Description: The Food industry involves agriculture, food processing, packaging, and distribution, focusing on safety, nutrition, and consumer convenience.

'Apparel & Fashion' - Description: The Apparel & Fashion industry encompasses the design, production, and retail of clothing, footwear, and accessories, driven by trends, innovation, and global economics.

'Cosmetic & Beauty' - Description: The Cosmetic & Beauty industry includes the development, marketing, and sale of skincare, haircare, makeup, and personal care products, emphasizing aesthetics, well-being, and innovation.

'Miscellaneous' - Description: The Miscellaneous industry covers diverse sectors not classified elsewhere, focusing on emerging trends, niche markets, and innovative services or products.
"""


# End buyer prompt
end_buyers = ["Sales", "Marketing", "HR", "Finance", "Tech & Data", "Legal", "Procurement", "Client support", "CSE", "ESG", "Communication", "Consumer"]
prompt_end_buyer =  f"""

You are given the description of a company retrieved from a company's website.

You will need to categorize the company within an End Buyer category according to the taxonomy below.

An end buyer is defined as the department of the persona that will be the main point of contact for the company when selling to them.

There can only be ONE end buyer. The answer needs to be concise and only can follow the taxonomy.

DO NOT come up with any taxonomy. STICK to the taxonomy below. 

Give your results in the format format JSON - 

'end_buyer': [end buyer] 

Here the taxonomy for each of the End Buyers - 

End Buyer:
Sales - Description: The Sales department focuses on generating revenue through client acquisition, relationship management, and selling products or services.

Marketing - Description: The Marketing department drives brand awareness, market research, and promotion strategies to attract and retain customers.

HR - Description: HR manages employee relations, recruitment, training, and organizational culture to support workforce efficiency and satisfaction.

Finance - Description: The Finance department oversees financial planning, management of company funds, accounting, and reporting to ensure fiscal health.

Tech & Data - Description: Tech & Data is responsible for IT infrastructure, software development, data analysis, and technological innovation to support business operations.

Legal - Description: The Legal department handles compliance, contracts, intellectual property, and legal disputes to protect the organization's interests.

Procurement - Description: Procurement manages sourcing, purchasing, and negotiating materials and services at optimal costs, while also overseeing internal process and resource planning to ensure organizational efficiency and cost-effectiveness.

Client support - Description: Client Support ensures customer satisfaction through assistance, problem resolution, and maintaining high service quality post-purchase.

CSE - Description: CSE aims to enhance customer loyalty and experience through proactive support, ensuring product or service value maximization.

ESG - Description: ESG focuses on company practices that promote environmental sustainability, social responsibility, and ethical governance.

Communication - Description: The Communication department manages internal and external messaging, public relations, and media to shape and convey the organization's narrative.

Consumer - Description: Consumers are the end-users in B2C companies who purchase products or services for personal use, driving demand and market trends based on their preferences and needs.

"""

# Physical store prompt
physical_stores = ["yes", "no"]
prompt_physical_store = f""" 
You are given the description of a company retrieved from a company's website.

You will need to categorize whether the company has physical stores available or not.

Give your results in the format format JSON by saying "yes" or "no", like this:

'physical_store': [yes or no]

"""

# Sales/Prodcut led prompt
sales_product_leds = ["Sales led", "Product led"]
prompt_before_salesprod = """
From the following scrapped text of a website, deduce whether this company is sales or product led.

Sales led means that the company has a 'demo' or 'book a call' type of button to check their services or product.
Product led means that the company has a 'sigh up', 'checkout' or 'buy now' button to self-serve the product/service.

The text will be poorly written so take that in mind. Don't explain your reasoning, just output whether its a Sales led or Product led company.

Ouput the text as a json like this:

{
    "sales_product_led": "Sales led" or "Product led"
}
"""

fundraising_states = ["VC Backed", "Public", "Bootstrapped",]
prompt_fundraising_states = """
From the following data, categorise the company's fundraising state within one of these categories:

VC backed,
Public,
Bootstrapped,

If no funding amount is seen, categorise bootstrapped. 
If there is some funding amount and the round (Series A, Series B...) specified, include VC backed.

Ouput the text as a JSON like this:

{
    "fundraising_state": "VC Backed" or "Public" or "Bootstrapped"
}

Here the data regarding funding: 
"""

ngo_tags = ["For-profit", "Non-profit"]
prompt_ngo_tag = """ 
You'll be given as input the industry of a company. Categorise if its "For-profit" or "Non-profit".

Output your answer in JSON like this: 

{
    "NGO_tag": "For-profit" or "Non-profit"
}

Here the industry to be classified: 
"""

# Helper prompts
organize_prompt = 'From the following scrapped text of a website explain what the business does and its core operations. Make some enfasis on their channels of selling. The text will be poorly written so take that in mind. Write everything in third person naming the company. Output only a description of the compnay using key words of the industry. Here the scrapped code/text from the companys website, be concise at all times: '
header_url= "\n Here the description of the company deducted from their website: "

# Helper functions
def truncate_string(input_string):
    if len(input_string) <= 3000:
        return input_string
    else:
        return input_string[:3000]

def format_url(url):
    if url.startswith("http://www."):
        url = url.replace("http://www.", "https://www.")
    elif url.startswith("http://"):
        url = url.replace("http://", "https://www.")
    elif url.startswith("www."):
        url = "https://" + url
    elif not url.startswith("https://"):
        url = "https://www." + url
    return url

# Business Status
def business_status(company_employees, company_founded_date):
    try:
        company_age = 2024 - company_founded_date
    except Exception:
        print('Founded date not provided or NaN.')
        company_age = 0
    
    if (company_employees < 200 and company_age <= 5) or company_employees < 200:
        return 'Startup'
    elif (201 <= company_employees <= 1000 and 3 <= company_age < 15) or 201 <= company_employees <= 1000:
        return 'MidMarket'
    elif (company_employees >= 1001 or company_age >= 15) or company_employees >= 1001:
        return 'Corporate'
    else:
        return 'Uncategorized'
    

# IndustryGPT 
exec = ThreadPoolExecutor(12)


def industryGPT(name, url, company_id=None, company_employees=None, company_founded_date=None, 
                linkedin_industry=None, founding_data=None, extra_descriptors=None):
    
    print('Enriching: ', name)
    print('With URL: ', url)
    print('Company ID: ', company_id)



    full_response = {

            "company_id": str(company_id),
            "metadata": {
                "timestamp": str(datetime.now()),
                "source": "industryGPT"
            },
            "company_profile": {
                "website": str(url),
                "n_employees": str(company_employees),
                "founded_date": str(company_founded_date),
                "business_status": None,
                "industry": None,
                "business_model": None,
                "end_buyer": None,
                "physical_store": 'no',
                "client_focus": None,
                "sales_product_led": 'Sales led',
                "fundraising_state": None,
                "NGO_tag": None,
                "description": None
            }

        }
    

    # Categorise business status
    if company_employees != None:
        try:
            b_status = business_status(company_employees, company_founded_date)
            full_response["company_profile"]["business_status"] = b_status
            print('Company categorised as: ', b_status)
        except Exception as e:
            print(e)
            print("Error categorising business_status.")
            return Exception
    else:
        b_status = 'Uncategorized'
        full_response["company_profile"]["business_status"] = b_status
        print('Company categorised as: ', b_status)
    
    scrapped_code = None

    try:
        url_text = retrieve_html(format_url(url))
        scrapped_code = url_text
        print('\n-> Retrieved text from website...')
    except Exception as e:
        print('Unaccessible URL as per error ->', e)
        print('Inputting description from LinkedIn.')
        scrapped_code = None
        url_text = extra_descriptors

    
    if len(url_text) > 30:
        print('-> Crafting company description...')
        description_openai = generate_response_gpt3(organize_prompt + truncate_string(url_text))
        print('\nDescription of the company: ', description_openai)

    else:
        print('Scrapped website or extra descriptors have less than 100 characters...')
        print('Trying to search on google a new page...')
        new_url = selenium_search(format_url(url))
        url_text = retrieve_html(new_url)
        description_openai = generate_response_gpt3(organize_prompt + truncate_string(url_text))
        print('\nDescription of the company: ', description_openai)

    # Save description
    full_response["company_profile"]["description"] = description_openai


    # Define specific industry
    if b_status == 'Startup':
        industry_categories = startup_industries
        selected_industries = ', '.join(industry_categories)

    if b_status == 'MidMarket':
        industry_categories = midmarket_industries
        selected_industries = ', '.join(industry_categories)

    if b_status == 'Corporate':
        industry_categories = corporate_industries
        selected_industries = ', '.join(industry_categories)
    
    if b_status == 'Uncategorized':
        industry_categories = startup_industries
        selected_industries = ', '.join(industry_categories)
    

    # Categorise industry & business Model
    response_industry = exec.submit(generate_response, (prompt_industry_business +
                                selected_industries +
                                header_url +
                                description_openai))
    
    # Categorise client Focus
    response_clientfocus = exec.submit(generate_response, (prompt_client_focus +
                                header_url +
                                description_openai))
    
    # Categorise end Buyer
    response_endbuyer = exec.submit(generate_response, (prompt_end_buyer +
                                header_url +
                                description_openai))
    
    if scrapped_code != None:
        response_physical_store = exec.submit(generate_response, (prompt_physical_store + 
                                header_url +
                                truncate_string(scrapped_code)))

        response_sales_product_led = exec.submit(generate_response_gpt3_json, (prompt_before_salesprod + 
                                header_url +
                                truncate_string(scrapped_code)))
        
        result_physical_store = response_physical_store.result()
        result_sales_product_led = response_sales_product_led.result()

        response_dict_physical_store = json.loads(result_physical_store)
        physical_store = response_dict_physical_store["physical_store"]

        response_dict_sales_product_led = json.loads(result_sales_product_led)
        sales_product_led = response_dict_sales_product_led["sales_product_led"]

        tries_physical_store = 0
        while physical_store not in physical_stores and tries_physical_store < 2:
            if tries_physical_store >= 2:
                print('Physical store not in category.')
                print('GPT failed twice, returning NaN in physical_store.')
                physical_store = None
                break
            print('Physical Store not in category.')
            print('Faulty Physical Store: ', physical_store)
            initial_question = (prompt_physical_store+ header_url + truncate_string(scrapped_code))
            system_answer = "Physical Store: " + physical_store
            feedback = "The Physical Store is not within the categories possible... retry please and stay within the provided taxonomy."
            # Resubmit the prompt
            retry_physical_store = exec.submit(generate_response_feedback, initial_question, system_answer, feedback)
            retry_physical_store_dict = retry_physical_store.result()
            retry_physical_store_dict_json = json.loads(retry_physical_store_dict)
            physical_store = retry_physical_store_dict_json["physical_store"]
            tries_physical_store += 1
        
        tries_sales_product_led = 0
        while sales_product_led not in sales_product_leds and tries_sales_product_led < 2:
            if tries_sales_product_led >= 2:
                print('Sales Product Led not in category.')
                print('GPT failed twice, returning NaN in physical_store.')
                sales_product_led = None
                break
            print('Sales Product Led not in category.')
            print('Faulty Sales Product Led: ', sales_product_led)
            initial_question = (prompt_before_salesprod+ header_url + truncate_string(scrapped_code))
            system_answer = "Sales Product Led: " + sales_product_led
            feedback = "The Sales Product Led is not within the categories possible... retry please and stay within the provided taxonomy."
            # Resubmit the prompt
            retry_sales_product_led = exec.submit(generate_response_feedback, initial_question, system_answer, feedback)
            retry_sales_product_led_dict = retry_sales_product_led.result()
            retry_sales_product_led_dict_json = json.loads(retry_sales_product_led_dict)
            sales_product_led = retry_sales_product_led_dict_json["sales_product_led"]
            tries_sales_product_led += 1

        full_response["company_profile"]["physical_store"] = physical_store
        full_response["company_profile"]["sales_product_led"] = sales_product_led

    if linkedin_industry != None:
        response_NGO_tag = exec.submit(generate_response_gpt3_json, (prompt_ngo_tag + linkedin_industry))
        result_NGO_tag = response_NGO_tag.result()

        response_dict_NGO_tag = json.loads(result_NGO_tag)
        NGO_tag = response_dict_NGO_tag["NGO_tag"]

        tries_NGO_tag = 0
        while NGO_tag not in ngo_tags and tries_NGO_tag < 2:
            if tries_NGO_tag >= 2:
                print('NGO tag not in category.')
                print('GPT failed twice, returning NaN in NGO_tag.')
                NGO_tag = None
                break
            print('NGO tag not in category.')
            print('Faulty NGO tag: ', NGO_tag)
            initial_question = (prompt_ngo_tag + linkedin_industry)
            system_answer = "NGO tag: " + NGO_tag
            feedback = "The tag is not within the categories possible... retry please and stay within the provided taxonomy."
            # Resubmit the prompt
            retry_NGO_tag = exec.submit(generate_response_feedback, initial_question, system_answer, feedback)
            retry_NGO_tag_dict = retry_NGO_tag.result()
            retry_NGO_tag_dict_json = json.loads(retry_NGO_tag_dict)
            NGO_tag = retry_NGO_tag_dict_json["NGO_tag"]
            tries_NGO_tag += 1
        
        full_response["company_profile"]["NGO_tag"] = NGO_tag
        
    if founding_data != None and founding_data != "":
        response_founding_data = exec.submit(generate_response_gpt3_json, (prompt_fundraising_states + founding_data))
        result_founding_data = response_founding_data.result()

        response_dict_founding_data  = json.loads(result_founding_data)
        fundraising_state = response_dict_founding_data["fundraising_state"]

        tries_fundraising_state = 0
        while fundraising_state not in fundraising_states and tries_fundraising_state < 2:
            if tries_fundraising_state >= 2:
                print('Fundraising state not in category.')
                print('GPT failed twice, returning NaN in NGO_tag.')
                fundraising_state = None
                break
            print('Fundraising state not in category.')
            print('Faulty Fundraising state: ', fundraising_state)
            initial_question = (prompt_fundraising_states + founding_data)
            system_answer = "Fundraising state: " + founding_data
            feedback = "The tag is not within the categories possible... retry please and stay within the provided taxonomy."
            # Resubmit the prompt
            retry_founding_data = exec.submit(generate_response_feedback, initial_question, system_answer, feedback)
            retry_founding_data_dict = retry_founding_data.result()
            retry_founding_data_dict_json = json.loads(retry_founding_data_dict)
            founding_data = retry_founding_data_dict_json["founding_data"]
            tries_fundraising_state += 1
        
        full_response["company_profile"]["fundraising_state"] = fundraising_state

    result_industry = response_industry.result()
    result_clientfocus = response_clientfocus.result()
    result_endbuyer = response_endbuyer.result()
    

    response_dict_industry = json.loads(result_industry)

    # Is the categorization correct for industry & business model? 
    industry = response_dict_industry["industry"]
    business_model = response_dict_industry["business_model"]


    tries_industry = 0
    while (industry not in industry_categories or business_model not in business_models) and tries_industry < 2:
        if tries_industry >= 2:
            print('Industry or Business Model not in category.')
            print('GPT failed twice, returning NaN in Industry & Business Model.')
            industry = None
            business_model = None
            break
        
        print('Industry or Business Model not in category.')
        print('Faulty Industry: ', industry)
        print('Faulty Business Model: ', business_model)

        initial_question = (prompt_industry_business + selected_industries + header_url + description_openai)
        system_answer = "Industry: " + industry + " Business Model: " + business_model
        feedback = "The Industry and/or Business Model is not within taxonomy... retry please and stay within taxonomy."
        # Resubmit the prompt
        retry_industry = exec.submit(generate_response_feedback, initial_question, system_answer, feedback)
        retry_industry_dict = retry_industry.result()
        retry_industry_dict_json = json.loads(retry_industry_dict)
        industry = retry_industry_dict_json["industry"]
        business_model = retry_industry_dict_json["business_model"]
        tries_industry += 1

    # Special categorization for ecomms
    tries_ecomm_ind = 0
    if business_model == 'Ecommerce':
        print('Business Model is Ecomm, categorising specifically. Previous industry: ', industry)
        while (industry not in ecomm_industries and tries_ecomm_ind <= 2) or industry == "Miscellaneous" and tries_ecomm_ind <= 1:
            selected_industries_ecomm = ', '.join(ecomm_industries)
            retry_ecomm_business_model = exec.submit(generate_response, (prompt_industry_business_ecomm +
                                                                            selected_industries_ecomm +
                                                                            header_url +
                                                                            description_openai))
            
            ecomm_business_model = retry_ecomm_business_model.result()
            response_dict_ecomm_business_model = json.loads(ecomm_business_model)
            industry = response_dict_ecomm_business_model["industry"]
            tries_ecomm_ind += 1

    # Save result industry & business model
    full_response["company_profile"]["industry"] = industry
    full_response["company_profile"]["business_model"] = business_model

    # Is the categorization correct for client focus? 
    response_dict_clientfocus = json.loads(result_clientfocus)
    client_focus = response_dict_clientfocus["client_focus"]
    
    tries_client_focus = 0
    while client_focus not in clients_focus and tries_client_focus < 2:
        if tries_client_focus >= 2:
            print('Client focus not in category.')
            print('GPT failed twice, returning NaN in Client focus.')
            client_focus = None
            break
        
        print('Client Focus not in category.')
        print('Faulty Client Focus: ', client_focus)
        initial_question = (prompt_client_focus+ header_url + description_openai)
        system_answer = "Client Focus: " + client_focus
        feedback = "The client focus is not within taxonomy... retry please and stay within the provided taxonomy."
        # Resubmit the prompt
        retry_clientfocus = exec.submit(generate_response_feedback, initial_question, system_answer, feedback)
        retry_clientfocus_dict = retry_clientfocus.result()
        retry_clientfocus_dict_json = json.loads(retry_clientfocus_dict)
        client_focus = retry_clientfocus_dict_json["client_focus"]
        tries_client_focus += 1
    
    # Save result client_focus
    full_response["company_profile"]["client_focus"] = client_focus   
    

    # Is the categorization correct for end buyer?
    response_dict_endbuyer = json.loads(result_endbuyer)
    end_buyer = response_dict_endbuyer["end_buyer"]

    tries_end_buyer = 0
    while end_buyer not in end_buyers and tries_end_buyer < 2:
        if tries_end_buyer >= 2:
            print('End buyer not in category.')
            print('GPT failed twice, returning NaN in end buyers.')
            end_buyer = None
            break

        print('End Buyer not in category.')
        print('Faulty End buyer: ', end_buyer)
        initial_question = (prompt_end_buyer+ header_url + description_openai)
        system_answer = "End Buyer: " + end_buyer
        feedback = "The end buyer is not within taxonomy... retry please and stay within the provided taxonomy."
        # Resubmit the prompt
        retry_endbuyer = exec.submit(generate_response_feedback, initial_question, system_answer, feedback)
        retry_endbuyer_dict = retry_endbuyer.result()
        retry_endbuyer_dict_json = json.loads(retry_endbuyer_dict)
        end_buyer = retry_endbuyer_dict_json["end_buyer"]
        tries_end_buyer += 1
        
    # Save result end_buyer
    full_response["company_profile"]["end_buyer"] = end_buyer
    

    full_response_json = json.dumps(full_response)
    json_string_pretty = json.dumps(full_response, indent=2)
    print('')
    print(json_string_pretty)
    print('--------------------------------')

    return full_response_json

# IndustryGPT Loop
def industryGPT_loop(name, url, company_id, employee_count=0, founded_date=0, linkedin_industry=None, founding_data=None,  extra_descriptors=None):
    tries = 1

    while tries <= 4:
        try:
            if tries <= 2:
                response = industryGPT(name, format_url(url), company_id, employee_count, founded_date, linkedin_industry, founding_data, extra_descriptors)

                if response == None:
                    print('Response is: ', response)
                    raise Exception
                else:
                    return response
            else:
                new_url = selenium_search(url)
                print('Trying with website:', format_url(format_url(new_url)))
                print('--------------------------------')
                response = industryGPT(name, new_url, company_id, employee_count, founded_date, linkedin_industry, founding_data, extra_descriptors)
                
                if response == None:
                    print('Response is: ', response)
                    raise Exception
                else:
                    return response

    
        except Exception as e:
            print('Error, exception as e: ', e)
            tries += 1
    
    return None


@functions_framework.http
def receive_request_industryGPT(request):
    # Get the stored API key from environment variable
    stored_api_key = os.environ.get('API_KEY_INDUSTRYGPT_2')

    # Extract API key from request headers
    request_api_key = request.headers.get('APOLO-API-KEY')

    # Check if the API keys match
    if not request_api_key:
        return json.dumps({'error': 'Missing APOLO-API-KEY, include it in the headers section of the API request.'}), 403

    if request_api_key != stored_api_key:
        return json.dumps({'error': 'Invalid APOLO-API-KEY, please check your inputted value or get in touch with the Apolo team for support.'}), 403
    
    # Ensure the request is JSON
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json and 'url' in request_json:
        # Extract parameters from JSON body
        name = request_json['name']
        url = request_json['url']
        company_id = request_json.get('company_id', '')
        employee_count = request_json.get('employee_count', 0)
        founded_date = request_json.get('founded_date', 0)
        linkedin_industry = request_json.get('linkedin_industry', None)
        founding_data = request_json.get('founding_data', None)
        extra_descriptors = request_json.get('extra_descriptors', None)
    elif request_args:
        # Extract parameters from query string
        name = request_args.get('name', '')
        url = request_args.get('url', '')
        company_id = request_args.get('company_id', '')
        employee_count = request_args.get('employee_count', 0)
        founded_date = request_args.get('founded_date', 0)
        linkedin_industry = request_json.get('linkedin_industry', None)
        founding_data = request_json.get('founding_data', None)
        extra_descriptors = request_args.get('extra_descriptors', None)
    else:
        return json.dumps({"error": "Missing 'name' and/or 'url parameter"}), 400

    try:
        # Call the industryGPT_loop function and return its result
        result = industryGPT_loop(name, url, company_id, employee_count, founded_date, linkedin_industry, founding_data, extra_descriptors)
        if result == None:
            raise Exception
        return json.dumps(result), 200
    
    except Exception as e:
        # Handle exceptions and return error message
        return json.dumps({'error': str(e)}), 500


