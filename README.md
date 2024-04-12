# IndustryGPT

IndustryGPT is a Python-based application designed to enrich company profiles by leveraging various API services to gather and synthesize data.

## Requirements

- Python 3.8+
- `requests` library
- Access to OpenAI API, Google Search API, and other specified APIs.
- An `.env` file configured with the required API keys.

## Setup

1. Ensure Python 3.8+ is installed on your machine.
2. Install the required Python packages:
   ```bash
   pip install requests python-dotenv
   ````
3. Create an .env file in the root directory of the project with the following content:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    GOOGLE_SEARCH_API=your_google_search_api_key_here
    SEARCH_ENGINE_ID=your_search_engine_id_here
    API_KEY_INDUSTRYGPT_2=your_industrygpt_2_api_key_here
    ````

## Calling the GCP function

To run the GCP function, find full documentation on the [API documentation Page](https://www.notion.so/apolo-smma/API-Documentation-for-industryGPT-9fc3948a038e48af93c9d51bb4a9da95?pvs=4)