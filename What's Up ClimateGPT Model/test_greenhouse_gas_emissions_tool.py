# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 20:06:23 2024

@author: Vishay Paka, Dontonio
"""

import nest_asyncio
nest_asyncio.apply()

import pandas as pd
import json
import asyncio
from greenhouse_gas_emissions_tool import GreenhouseGasEmissionsTool

# Initialize the tool
tool = GreenhouseGasEmissionsTool()

# Define a function to check results for each test case and handle non-serializable objects
def print_test_result(description, result):
    # Convert any pandas Series to a list or dictionary for JSON compatibility
    for key, value in result.items():
        if isinstance(value, pd.Series):
            result[key] = value.tolist()  # Convert Series to list
        elif isinstance(value, pd.DataFrame):
            result[key] = value.to_dict(orient="records")  # Convert DataFrame to list of dicts
    print(f"\n{description}")
    print(json.dumps(result, indent=2))

# Define an async function to call each method
async def main():
    # Test cases for each function
    # Comment other test cases when you want to run any particular one, as the results for some of the test cases are huge.
    
    # 1. Test get_country_emissions
    result = await tool.run_impl(action="country_emissions", country="United States", year=2000)
    print_test_result("Country emissions for United States in 2000:", result)
    
    # 2. Test aggregate_emissions_by_region
    result = await tool.run_impl(action="region_aggregation", region="Middle East")
    print_test_result("Region aggregation for Middle East:", result)
    
    # 3. Test emissions_trend_country
    result = await tool.run_impl(action="emissions_trend", country="Ghana")
    print_test_result("Emissions trend for Ghana:", result)

    # 4. Test compare_countries
    result = await tool.run_impl(action="compare_countries", country="Russia", country2="China")
    print_test_result("Comparison of emissions between Russia and China:", result)
    
    # 5. Test total_global_emissions
    result = await tool.run_impl(action="total_global_emissions")
    print_test_result("Total global emissions:", result)

    # 6. Test total_emissions_by_gas
    result = await tool.run_impl(action="total_emissions_by_gas", gas_type="CH4")
    print_test_result("Total emissions by gas (CH4):", result)

    # 7. Test emissions_by_region
    result = await tool.run_impl(action="emissions_by_region")
    print_test_result("Emissions by region:", result)

    # 8. Test top_n_countries_by_emissions
    result = await tool.run_impl(action="top_n_countries_by_emissions", year=2000, top_n=2)
    print_test_result("Top 2 countries by emissions for the year 2000:", result)
    
    # 9. Test percentage_change_emissions
    result = await tool.run_impl(action="percentage_change_emissions", country="United States", start_year=2000, end_year=2001)
    print_test_result("Percentage change in emissions for United States between 2000 and 2001:", result)
    
    # 10. Test highest_emissions_year
    result = await tool.run_impl(action="highest_emissions_year", country="China")
    print_test_result("Highest emissions year for China:", result)

    # 11. Test lowest_emissions_year
    result = await tool.run_impl(action="lowest_emissions_year", country="Japan")
    print_test_result("Lowest emissions year for Japan:", result)
    
    # 12. Test cumulative_emissions
    result = await tool.run_impl(action="cumulative_emissions", country="United States", start_year=2000, end_year=2001)
    print_test_result("Cumulative emissions for United States between 2000 and 2001:", result)
    
# Run the async main function
asyncio.run(main())
