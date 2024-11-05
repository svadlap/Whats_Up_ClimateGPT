import nest_asyncio
import json
import asyncio
from organic_soil_emissions_tool import OrganicSoilEmissionsTool  # Ensure this points to the actual file name

# Apply nest_asyncio to handle nested asyncio calls
nest_asyncio.apply()

# Initialize the tool
tool = OrganicSoilEmissionsTool()

def print_test_result(description, result):
    print(f"\n{description}")
    if "forecast" in result and isinstance(result["forecast"], list):
        # Print forecast values with year labels if forecast data is available
        for year, value in zip(range(2022, 2032), result["forecast"]):
            print(f"{year}: {round(value)}")  # Rounded to nearest whole number
    else:
        # Print result as JSON if not a forecast, or display an error if needed
        print(json.dumps(result, indent=2))
        if "message" in result:
            print("Error message:", result["message"])

# Define the main async function to run tests
async def main():
    # 1. Rank areas with the highest emissions each year
    result = await tool.run_impl(action="list_highest_emissions", element="Emissions (CO2)", start_year=2010, end_year=2020)
    print_test_result("Areas with the highest CO2 emissions each year from 2010 to 2020:", result)

    # 2. Calculate average annual emissions for an area over a decade
    result = await tool.run_impl(action="average_annual_emissions", area="Poland", element="Emissions (CO2)", start_year=2010, end_year=2020)
    print_test_result("Average CO2 emissions in Poland from 2010 to 2020:", result)

    # 3. Estimate cumulative emissions over a date range for an area
    result = await tool.run_impl(action="cumulative_emissions", area="Argentina", element="Emissions (CO2)", start_year=2010, end_year=2018)
    print_test_result("Total CO2 emissions in Argentina from 2010 to 2018:", result)

    # 4. Simulate future emissions based on historical trends
    result = await tool.run_impl(
        action="long_term_forecast", 
        area="Romania", 
        element="Emissions (CO2)", 
        projection_years=10
    )
    print_test_result("10-year projection for CO2 emissions in Romania (2022-2031):", result)
    
    # 5. Calculate trends in CO2 and N2O emissions over a specified time period for a country
    result = await tool.run_impl(
        action="calculate_trends",
        area="Brazil",
        start_year=2010,
        end_year=2020
    )
    print_test_result("Trends in CO2 and N2O emissions in Brazil from 2010 to 2020:", result)

    # 6. Compare emissions between specified countries over a specified time range
    result = await tool.run_impl(
        action="compare_emissions",
        areas=["Argentina", "Brazil", "Poland"],
        start_year=2010,
        end_year=2020
    )
    print_test_result("Emissions comparison between Argentina, Brazil, and Poland from 2010 to 2020:", result)

    # 7. Get summary data for a specific area and time range
    result = await tool.run_impl(
        action="get_summary_data",
        area="Japan",
        start_year=2010,
        end_year=2020
    )
    print_test_result("Summary of CO2 and N2O emissions in Japan from 2010 to 2020:", result)

    # 8. Find missing data points for a specified area and element
    result = await tool.run_impl(
        action="find_missing_data",
        area="Uzbekistan",
        element="Emissions (CO2)"
    )
    print_test_result("Missing data years for CO2 emissions in Austria:", result)

    #9. Analyze correlation between CO2 and N2O emissions for a specific area
    result = await tool.run_impl(
        action="analyze_correlation",
        area="Sweden",
        start_year=2000,
        end_year=2015
    )
    print_test_result("Correlation between CO2 and N2O emissions in Sweden from 2000 to 2015:", result)

    # 10. Compare cumulative emissions for specific conditions across multiple countries
    result = await tool.run_impl(
        action="compare_emissions_with_conditions",
        areas=["Brazil", "Bangladesh", "Denmark"],
        element="Emissions (CO2)",
        item="Cropland organic soils",
        source="FAO TIER 1",
        unit="kt",
        start_year=2010,
        end_year=2021
    )
    print_test_result("Emissions comparison across Brazil, Bangladesh, and Denmark with specified conditions:", result)

# Run the async main function
asyncio.run(main())
