# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 15:29:20 2024

@author: Dontonio
"""

import asyncio
from greenhouse_gas_emissions_tool import GreenhouseGasEmissionsTool

async def main():
    # Create an instance of the tool
    emissions_tool = GreenhouseGasEmissionsTool()

    # Example: Get Emissions for a Specific Country and Year
    result = await emissions_tool.run_impl(
        file_path='total-global-greenhouse-gas-emissions.xlsx',
        action='top_n_countries_by_emissions',
        year=2020,
        n=50,
        gas_type='CO2'
    )
    print("Country Emissions:", result)

    # Example: Aggregate Emissions by Region
    result = await emissions_tool.run_impl(
        file_path='total-global-greenhouse-gas-emissions.xlsx',
        action='region_aggregation',
        region='Central Europe',
        gas_type='CO2'
    )
    print("Region Aggregation:", result)

    # Example: Get Emissions Trend for a Country
    result = await emissions_tool.run_impl(
        file_path='total-global-greenhouse-gas-emissions.xlsx',
        action='emissions_trend',
        country='China'
    )
    print("Emissions Trend for China:", result)

# Run the main function using asyncio
if __name__ == "__main__":
    asyncio.run(main())
