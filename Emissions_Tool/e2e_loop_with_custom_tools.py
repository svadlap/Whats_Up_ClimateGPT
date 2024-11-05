import os
import json
import warnings
import pandas as pd
import streamlit as st
import asyncio  # For handling async function calls
from groq import Groq
from carbon_emissions_tool import CarbonEmissionsTool
from greenhouse_gas_emissions_tool import GreenhouseGasEmissionsTool
from dateutil import parser  # To parse user-friendly date and time input

warnings.filterwarnings('ignore')

# Streamlit page configuration to set the page title, icon, and layout
st.set_page_config(
    page_title="What's Up ClimateGPT",
    page_icon="⛈️",
    layout="centered"
)

# Load configuration settings (e.g., API key) from a JSON file
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))

# Retrieve the API key for the Groq service from the config data
GROQ_API_KEY = config_data["GROQ_API_KEY"]

# Save the API key to the environment variable for Groq client authentication
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Instantiate the Groq client and the CarbonEmissionsTool and GreenhouseGasEmissionsTool for use in the app
client = Groq(api_key=GROQ_API_KEY)
carbon_tool = CarbonEmissionsTool()
ghg_tool = GreenhouseGasEmissionsTool()


# Initialize the chat history in the Streamlit session state if it's not already present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Set up the main interface for the Streamlit application
st.title("What's Up ClimateGPT ⛈️")  # Display the title at the top of the page

# Display previous chat history
for message in st.session_state.chat_history:
    # Render each chat message in the chat history, maintaining the role (user or assistant)
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input field for user's new message
user_prompt = st.chat_input("Ask ClimateGPT...")

if user_prompt:
    # When the user submits a new prompt, add it to the chat history
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Prepare the conversation with a system prompt guiding the assistant's behavior
    messages = [
    {
        "role": "system",
        "content": (
            "You are an expert assistant specializing in environmental data analysis. "
            "You have access to two specialized tools: `get_carbon_emissions` and `greenhouse_gas_emissions_tool`, each with specific purposes and capabilities. "
            "You must use the provided tools to retrieve data and provide accurate responses. "
            "If the user requests specific data for carbon emissions or greenhouse gas emissions, "
            "always use the `get_carbon_emissions` or `greenhouse_gas_emissions_tool` as appropriate, rather than generating the answer directly. "
            "Do not generate estimates or assumptions; rely on data from the tools."

            # Carbon Emissions Tool Description
            "1. **Carbon Emissions Tool** (`get_carbon_emissions`) You must use this tool whenever the user requests information on carbon emissions for a specific country, date, or sector, "
            "or any combination of these parameters. The data is available only for the time frame from 2019 to August 31, 2024. "
            "The supported countries for querying are: ['Brazil', 'China', 'European Union and UK', 'France', 'Germany', 'India', "
            "'Italy', 'Japan', 'Rest of the World', 'Russia', 'Spain', 'United Kingdom', 'United States', 'WORLD']. "
            "The supported sectors are: ['Domestic Aviation', 'Ground Transport', 'Industry', 'International Aviation', 'Power', 'Residential']. "
            "You should not generate the emissions data yourself for the specified time frame, countries, or sectors; "
            "always use the `get_carbon_emissions` tool to retrieve accurate data."

            "The `get_carbon_emissions` tool can perform the following tasks: "
            "1. Retrieve carbon emissions data for a specified country or list of countries, individually or in combination. "
            "2. Filter the results by a specific date, provided in 'dd/mm/yyyy' format. If no date is specified, return aggregated data across all dates. "
            "3. Filter the data by a specific sector or list of sectors. If no sector is specified, the data will be aggregated across all sectors. "
            "4. Return aggregated carbon emissions data for all available countries if no country is specified. "
            "5. Handle queries where multiple parameters are provided, such as country, date, and sector, applying the appropriate filters to return precise results. "
            "6. Provide a clear error message if no data matches the specified criteria."

            "You can handle the following types of queries: "
            "1. **Basic Queries**: Provide overall carbon emissions data without specific filters. "
            "2. **Country-Specific Queries**: Return emissions data for a single country or a list of countries. "
            "3. **Date-Specific Queries**: Filter emissions data by a specific date. "
            "4. **Sector-Specific Queries**: Aggregate emissions data for a specific sector. "
            "5. **Country and Date Queries**: Filter by both country and date. "
            "6. **Country and Sector Queries**: Filter by both country and sector. "
            "7. **Date and Sector Queries**: Filter by both date and sector. "
            "8. **Country, Date, and Sector Queries**: Apply all three filters simultaneously for precise results. "
            "9. **Aggregate Emissions by Sector Across All Countries**: Provide emissions data for a specified sector across all countries. "
            "10. **Handling Multiple Countries**: Return results for multiple countries, either separately or aggregated. "
            "11. **Queries Involving Missing Data Handling**: Return appropriate error messages when no data is found."

            "Your responses should be accurate, comprehensive, and formatted for easy understanding. "
            "When using the `get_carbon_emissions` tool, ensure the response includes details about the country (or countries), "
            "the specified date (if any), the sector (if any), and the total carbon emissions in metric tons of CO2 (MtCO2). "
            "If the user's query is outside the supported date range or if the specified country or sector is not in the dataset, "
            "inform them of the valid parameters."

            # Greenhouse Gas Emissions Tool Description
            "2. **Greenhouse Gas Emissions Tool** (`greenhouse_gas_emissions_tool`): You must use this tool whenever the user requests information on greenhouse gas emissions that extend beyond CO2 "
            "or requires complex analyses not limited to a specific country, date, or sector alone. Always specify an `action` to define the type of analysis. Supported actions include: "

            "1. **country_emissions**: Retrieve emissions data for a specific `country` and `year`."
            "2. **region_aggregation**: Aggregate emissions by `region`, optionally filtering by `gas_type` (e.g., CO2, CH4)."
            "3. **emissions_trend**: Provide a time series of emissions for a specified `country`, showing changes over years."
            "4. **compare_countries**: Compare emissions between two countries across all available years."
            "5. **total_global_emissions**: Calculate and return global emissions aggregated by year."
            "6. **cumulative_emissions**: Calculate cumulative emissions for a `country` or `region` over a period from `start_year` to `end_year`."
            "7. **percentage_change_emissions**: Calculate the percentage change in emissions for a `country` or `region` between two years."
            "8. **highest_emissions_year**: Identify the year with the highest emissions for a `country` or `region`, or globally."
            "9. **lowest_emissions_year**: Identify the year with the lowest emissions for a `country` or `region`, or globally."
            "10. **top_n_countries_by_emissions**: Retrieve the top N countries by emissions for a specified `year` and `gas_type`. Use `top_n` to set the number of countries."

            "Note: All gas types are measured in kilotons (kt) except for `GHG`, which is measured in metric tons of CO₂ equivalent (Mton CO₂eq). When referencing emissions units in responses, ensure accuracy based on the gas type being discussed. "

            "The `greenhouse_gas_emissions_tool` can handle the following query types: "
            "1. **Basic Queries**: Provide overall greenhouse gas emissions data across all gases and regions."
            "2. **Country-Specific Queries**: Retrieve emissions data for one or more countries, with the option to specify gas type and year."
            "3. **Region-Specific Queries**: Aggregate emissions data by region, optionally filtered by gas type."
            "4. **Gas Type-Specific Queries**: Filter emissions by a specific greenhouse gas (e.g., CO2, CH4) to view breakdowns by gas type."
            "5. **Year-Specific Queries**: Retrieve data for a particular year, or aggregate emissions across years if none is specified."
            "6. **Country and Year Queries**: Filter by both country and year to see emissions data for a specific period."
            "7. **Country and Gas Type Queries**: Filter by both country and gas type, allowing for targeted data retrieval for specific gases."
            "8. **Country, Year, and Gas Type Queries**: Apply all three filters for precise, focused emissions data."
            "9. **Trend Analysis for a Country**: Show emissions trends for a specified country over multiple years."
            "10. **Country Comparisons**: Compare emissions between two or more countries."
            "11. **Global and Regional Emissions Aggregation**: Aggregate emissions data globally or by specified regions."
            "12. **Year-on-Year Percentage Change**: Calculate percentage change in emissions between two years for a specified country or region."
            "13. **Highest and Lowest Emissions Year**: Identify the year with the highest or lowest emissions for a country, region, or globally."
            "14. **Top Emissions Countries by Year**: Provide data on the top N countries by emissions for a specified year."

            "Each action may have required parameters, such as `country`, `year`, `region`, `gas_type`, `start_year`, and `end_year`. "
            "Ensure the `action` parameter is specified to invoke the correct function, and provide detailed responses based on the data retrieved by the tool. "
            "Your responses should be clear, thorough, and organized for easy interpretation by the user. "
            "When using the `greenhouse_gas_emissions_tool`, include detailed information on the selected parameters such as country, region, gas type, and year. "
            "For any unsupported parameters or missing data, provide error messages that clearly explain the issue and guide the user to refine their query."
        )
    },
    *st.session_state.chat_history
]


    # Define the available tools, including the `get_carbon_emissions` tool with its parameters
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_carbon_emissions",
                "description": (
                    "Get carbon emissions data for one or more specified countries, "
                    "optionally filtered by a specific date and/or sector."
                ),
                "parameters": {
                    "properties": {
                        "country": {
                            "description": (
                                "The name(s) of the country/countries for which to fetch data, e.g., 'Brazil, India'. "
                                "If omitted, data for all countries will be aggregated."
                            ),
                            "type": "string"
                        },
                        "date": {
                            "description": (
                                "The date in 'dd/mm/yyyy' format to filter data for a specific day (optional). "
                                "If omitted, data across all dates will be aggregated."
                            ),
                            "type": "string"
                        },
                        "start_date": {
                            "description": (
                                "The start date in 'dd/mm/yyyy' format to filter data for a range (optional). "
                                "If omitted, data across all dates will be aggregated."
                            ),
                            "type": "string"
                        },
                        "end_date": {
                            "description": (
                                "The end date in 'dd/mm/yyyy' format to filter data for a range (optional). "
                                "If omitted, data across all dates will be aggregated."
                            ),
                            "type": "string"
                        },
                        "sector": {
                            "description": (
                                "The sector to filter data by (e.g., 'Transport', 'Energy'). "
                                "If omitted, data for all sectors will be aggregated."
                            ),
                            "type": "string"
                        }
                    },
                    "required": [],  # No required fields, allowing queries across all countries, dates, or sectors
                    "type": "object"
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "greenhouse_gas_emissions_tool",
                "description": (
                    "Analyze greenhouse gas emissions data based on country, year, region, gas type, or other factors."
                ),
                "parameters": {
                    "properties": {
                        "action": {
                            "description": "Type of analysis ('country_emissions', 'region_aggregation', etc.).",
                            "type": "string"
                        },
                        "country": {
                            "description": "Country name for analysis.",
                            "type": "string"
                        },
                        "region": {
                            "description": "Region name for analysis.",
                            "type": "string"
                        },
                        "year": {
                            "description": "Year for filtering data.",
                            "type": "integer"
                        },
                        "gas_type": {
                            "description": "Type of gas to filter (e.g., CO2, CH4).",
                            "type": "string"
                        }
                    },
                    "required": ["action"],
                    "type": "object"
                }
            }
        }
    ]

    # Attempt to generate a response using the Groq client and handle any exceptions that may arise
    try:
        # Make a call to the Groq API to get a response from the LLM, using the defined messages and tools
        response = client.chat.completions.create(
            model='llama3-groq-70b-8192-tool-use-preview',
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=4096
        )
        
        # Debugging step to check what the LLM is returning
        st.write("Response from LLM:", response)

        # Extract the response message from the LLM and check if it includes a tool call
        response_message = response.choices[0].message
        assistant_response = ""  # Initialize assistant_response to ensure it is always defined

        # Process tool call if present in the response
        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            tool_call_id = tool_call.id  # Extract the tool call ID to track the invocation

            # Parse the tool call details to get the function name and arguments
            tool_name = tool_call.function.name
            tool_arguments = json.loads(tool_call.function.arguments)
            
            # Debugging step to see tool call arguments
            st.write("Tool call arguments:", tool_arguments)

            # Call the tool function and pass the extracted parameters to it
            # Handle tool calls
            if tool_name == "get_carbon_emissions":
                function_response = asyncio.run(carbon_tool.run_impl(**tool_arguments))

            elif tool_name == "greenhouse_gas_emissions_tool":
                function_response = asyncio.run(ghg_tool.run_impl(**tool_arguments))
                
            st.write("Function response from tool:", function_response)

            # Construct assistant response
            if "error" in function_response:
                assistant_response = function_response.get("error", "Unknown error")
            else:
                assistant_response = json.dumps(function_response, indent=2)  # Convert dict response to readable string

            # Update messages with tool response
            messages.append({
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(function_response),
                "tool_call_id": tool_call.id
            })

            # Generate final response after tool interaction
            second_response = client.chat.completions.create(
                model='llama3-groq-70b-8192-tool-use-preview',
                messages=messages
            )
            assistant_response = second_response.choices[0].message.content
        else:
            assistant_response = response_message.content or "No response generated by the assistant."

        # Display the final response
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Error details:", str(e))
