# -*- coding: utf-8 -*-
"""
Test file for WeatherDataTool

Created on: Sat Nov 18, 2024

Description: Test cases for WeatherDataTool fetching data from the OpenWeather API

@author: Vishay Paka
"""

import nest_asyncio
nest_asyncio.apply()

import json
import asyncio
from current_weather_data_tool import WeatherDataTool

# Initialize the tool
weather_tool = WeatherDataTool()

# Define a function to check results for each test case and handle non-serializable objects
def print_test_result(description, result):
    print(f"\n{description}")
    print(json.dumps(result, indent=2))

# Define an async function to call each method
async def main():
    # Test cases for each function
    
    # 1. Test current_weather for a city
    result = await weather_tool.run_impl(action="current_weather_data", city="Fairfax")
    print_test_result("Current weather for Fairfax:", result)
    
    # 2. Test comfort_index for a city
    result = await weather_tool.run_impl(action="comfort_index", city="Fairfax")
    print_test_result("Comfort index for Fairfax:", result)
    
    # 3. Test fog_risk for a city
    result = await weather_tool.run_impl(action="fog_risk", city="Fairfax")
    print_test_result("Fog risk for Fairfax:", result)
    
    # 4. Test current_weather for a city with low temperatures
    result = await weather_tool.run_impl(action="current_weather_data", city="Reykjavik")
    print_test_result("Current weather for Reykjavik:", result)
    
    # 5. Test comfort_index for a city with high humidity
    result = await weather_tool.run_impl(action="comfort_index", city="Singapore")
    print_test_result("Comfort index for Singapore:", result)
    
    # 6. Test fog_risk for a city with moderate fog risk
    result = await weather_tool.run_impl(action="fog_risk", city="San Francisco")
    print_test_result("Fog risk for San Francisco:", result)
    
    # 7. Test current_weather for an invalid city to check error handling
    result = await weather_tool.run_impl(action="current_weather_data", city="ytuyguv")
    print_test_result("Current weather for invalid city 'ytuyguv':", result)

    # 8. Test comfort_index for an invalid city to check error handling
    result = await weather_tool.run_impl(action="comfort_index", city="qwerty")
    print_test_result("Comfort index for invalid city 'qwerty':", result)

    # 9. Test fog_risk for an invalid city to check error handling
    result = await weather_tool.run_impl(action="fog_risk", city="ImaginaryPlace")
    print_test_result("Fog risk for invalid city 'ImaginaryPlace':", result)
    
# Run the async main function
asyncio.run(main())
