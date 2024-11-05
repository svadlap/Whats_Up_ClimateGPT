# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:53:35 2024

@author: Dontonio
"""

import pandas as pd
import json
from typing import Dict
from custom_tools import SingleMessageCustomTool
from llama_stack_client.types.tool_param_definition_param import ToolParamDefinitionParam

# Load the data globally, allowing access across all instances
# This DataFrame (df) will be accessible across the GreenhouseGasEmissionsTool class
df = pd.read_excel('total-global-greenhouse-gas-emissions.xlsx')

# Drop any rows with missing values to ensure data consistency
# This step helps avoid errors during analysis by working only with complete data
df.dropna(inplace=True)

# Ensure the 'Year' column is of integer type for uniformity in processing and comparisons
df['Year'] = df['Year'].astype(int)

class GreenhouseGasEmissionsTool(SingleMessageCustomTool):
    """
    Custom tool to perform analysis on greenhouse gas emissions data.

    This class inherits from SingleMessageCustomTool, enabling integration
    with Llama models for data analysis. It provides multiple methods for
    processing greenhouse gas emissions data based on various parameters,
    such as country, region, and specific gases.
    """

    def get_name(self) -> str:
        """Return the name of the tool."""
        return "greenhouse_gas_emissions_tool"

    def get_description(self) -> str:
        """Return a description of what the tool does."""
        return "Perform analysis on greenhouse gas emissions data."

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        """
        Define the parameters the tool expects. These parameters guide the type
        of analysis to be performed and specify the required dataset and filters.

        Returns:
        - Dict[str, ToolParamDefinitionParam]: Dictionary defining the expected
          parameters and their descriptions for each method in this tool.
        """
        return {
            "action": ToolParamDefinitionParam(
                param_type="str",
                description="Type of analysis to perform: 'country_emissions', 'region_aggregation', etc.",
                required=True,
            ),
            "country": ToolParamDefinitionParam(
                param_type="str",
                description="Country name for analysis (if applicable).",
                required=False,
            ),
            "region": ToolParamDefinitionParam(
                param_type="str",
                description="Region name for analysis (if applicable).",
                required=False,
            ),
            "year": ToolParamDefinitionParam(
                param_type="int",
                description="Year for filtering data (if applicable).",
                required=False,
            ),
            "gas_type": ToolParamDefinitionParam(
                param_type="str",
                description="Filter by specific gas type (if applicable).",
                required=False,
            ),
        }

    async def run_impl(self, action: str, country: str = None, region: str = None, year: int = None, gas_type: str = None, start_year: int = None, end_year: int = None, top_n: int = 10):
        """
        Main function to execute the requested analysis based on the provided action.
        This method orchestrates various sub-functions based on the analysis type
        requested by the user and calls appropriate helper functions for execution.

        Parameters:
        - action: The type of analysis requested (e.g., 'country_emissions', 'region_aggregation').
        - country: (Optional) Name of the country for country-specific analysis.
        - region: (Optional) Name of the region for region-based analysis.
        - year: (Optional) Year for filtering data.
        - gas_type: (Optional) Gas type filter (e.g., CO2, CH4).
        - start_year, end_year: (Optional) Range of years for time series analysis.
        - n: (Optional) Number of top countries to return (used in some analyses).
        """
        
        # Helper function to get emissions for a specific country and year.
        def get_country_emissions(country, year):
            """
            Fetches emissions data for a specific country and year.

            Args:
            - country (str): Name of the country for which to retrieve emissions.
            - year (int): The year of interest.

            Returns:
            - dict: A dictionary containing emissions data for the specified
                    country and year. If no data is available, a message is returned.
            """
            result = df[(df['Country'] == country) & (df['Year'] == year)]
            if not result.empty:
                return {
                    "country": country,
                    "year": year,
                    "emissions": result['Value'],
                }
            return {"error": f"No data available for {country} in {year}"}

        # Helper function to aggregate emissions by region and optionally filter by gas type.
        def aggregate_emissions_by_region(region, gas_type=None):
            """
            Aggregates emissions for a region across all years, with optional filtering by gas type.

            Args:
            - region (str): Region name.
            - gas_type (str, optional): Type of gas for which emissions should be filtered (e.g., CO2, CH4).

            Returns:
            - dict: Aggregated emissions per year for the specified region,
                    with optional filtering by gas type.
            """
            filtered_data = df[df['World_Region'] == region]
            if gas_type:
                filtered_data = filtered_data[filtered_data['Substance'] == gas_type]
            if not filtered_data.empty:
                return {
                    "region": region, 
                    "gas_type": gas_type,
                    "yearly_emissions": filtered_data.groupby('Year')['Value'].sum().to_dict()
                }
            return {"error": f"No data available for {region}"}

        # Helper function to get the trend of emissions over time for a specific country.
        def emissions_trend_country(country):
            """
            Retrieves emissions trend for a country over available years.

            Args:
            - country (str): Name of the country.

            Returns:
            - dict: Yearly emissions data for the country.
            """
            trend = df[df['Country'] == country].groupby('Year')['Value'].sum().reset_index()
            return {
                "country": country,
                "trend": trend.to_dict(orient='records')
            } if not trend.empty else {"error": f"No data available for {country}"}

        # Helper function to compare emissions between two countries.
        def compare_countries(country1, country2):
            """
            Compares emissions data for two countries across all years.

            Args:
            - country1 (str): Name of the first country.
            - country2 (str): Name of the second country.

            Returns:
            - dict: Side-by-side comparison of yearly emissions for both countries.
            """
            data1 = df[df['Country'] == country1].groupby('Year')['Value'].sum().reset_index()
            data2 = df[df['Country'] == country2].groupby('Year')['Value'].sum().reset_index()
            if not data1.empty and not data2.empty:
                comparison = pd.merge(data1, data2, on='Year', suffixes=(f'_{country1}', f'_{country2}'))
                return {
                    "country_1": country1,
                    "country_2": country2,
                    "comparison": comparison.to_dict(orient='records')
                }
            return {"error": f"No data available for comparison between {country1} and {country2}"}

        # Helper function to calculate total global emissions across all years.
        def total_global_emissions():
            """
            Calculates total global emissions across all years.

            Returns:
            - dict: Global emissions aggregated by year.
            """
            global_emissions = df.groupby('Year')['Value'].sum().reset_index()
            return {
                "total_global_emissions": global_emissions.to_dict(orient='records')
            }

        # Helper function to get total emissions for a specific type of gas.
        def total_emissions_by_gas(gas_type):
            """
            Calculates emissions for a specific gas type across all years.

            Args:
            - gas_type (str): Type of greenhouse gas (e.g., CO2, CH4).

            Returns:
            - dict: Total emissions per year for the specified gas type.
            """
            filtered_data = df[df['Substance'] == gas_type]
            total_emissions = filtered_data.groupby('Year')['Value'].sum().reset_index()
            return {
                "gas_type": gas_type,
                "yearly_emissions": total_emissions.to_dict(orient='records')
            }

        # Helper function to retrieve emissions grouped by region and year.
        def emissions_by_region():
            """
            Retrieves emissions data by region for each year.

            Returns:
            - dict: Emissions data grouped by region and year.
            """
            emissions = df.groupby(['World_Region', 'Year'])['Value'].sum().reset_index()
            return {
                "emissions_by_region": emissions.to_dict(orient='records')
            }

        # Helper function to retrieve the top N countries by emissions in a specific year.
        def top_n_countries_by_emissions(year, top_n=10, gas_type=None):
            """
            Fetches the top N countries by emissions for a given year.

            Args:
            - year (int): Year of interest.
            - n (int): Number of top countries to retrieve (default is 10).
            - gas_type (str, optional): Specific gas type filter.

            Returns:
            - dict: Top N countries by emissions for the specified year.
            """
            filtered_data = df[df['Year'] == year]
            if gas_type:
                filtered_data = filtered_data[filtered_data['Substance'] == gas_type]
            top_countries = filtered_data.groupby('Country')['Value'].sum().nlargest(top_n).reset_index()
            return {
                "year": year,
                "gas_type": gas_type or "All",
                "top_n_countries": top_countries.to_dict(orient='records')
            }
        
        # Helper function to calculate the percentage change in emissions over a period.
        def percentage_change_emissions(country=None, region=None, start_year=None, end_year=None):
            """
            Calculates percentage change in emissions between two years for a country or region.

            Args:
            - country (str, optional): Country name.
            - region (str, optional): Region name.
            - start_year (int): Start year.
            - end_year (int): End year.

            Returns:
            - dict: Percentage change in emissions over the specified period.
            """
            if country:
                data = df[(df['Country'] == country) & (df['Year'].isin([start_year, end_year]))]
            elif region:
                data = df[(df['World_Region'] == region) & (df['Year'].isin([start_year, end_year]))]
            else:
                data = df[df['Year'].isin([start_year, end_year])]
            emissions_by_year = data.groupby('Year')['Value'].sum().reset_index()
            if emissions_by_year.shape[0] == 2:
                start_value = emissions_by_year[emissions_by_year['Year'] == start_year]['Value'].values[0]
                end_value = emissions_by_year[emissions_by_year['Year'] == end_year]['Value'].values[0]
                percentage_change = ((end_value - start_value) / start_value) * 100
                return {
                    "start_year": start_year,
                    "end_year": end_year,
                    "percentage_change": percentage_change
                }
            return {"error": "Data not available for the specified years."}

        # Helper function to find the year with the highest emissions for a country or region.
        def highest_emissions_year(country=None, region=None):
            """
            Finds the year with the highest emissions for a given country, region, or globally.

            Args:
            - country (str, optional): Country name.
            - region (str, optional): Region name.

            Returns:
            - dict: Year and emissions value with the highest emissions.
            """
            data = df
            if country:
                data = df[df['Country'] == country]
            elif region:
                data = df[df['World_Region'] == region]
            highest_year = data.groupby('Year')['Value'].sum().idxmax()
            highest_value = data.groupby('Year')['Value'].sum().max()
            return {
                "highest_emissions_year": highest_year,
                "highest_emissions_value": highest_value
            }
        
        # Helper function to find the year with the lowest emissions for a country or region.
        def lowest_emissions_year(country=None, region=None):
            """
            Finds the year with the lowest emissions for a given country, region, or globally.

            Args:
            - country (str, optional): Country name.
            - region (str, optional): Region name.

            Returns:
            - dict: Year and emissions value with the lowest emissions.
            """
            data = df
            if country:
                data = df[df['Country'] == country]
            elif region:
                data = df[df['World_Region'] == region]
            lowest_year = data.groupby('Year')['Value'].sum().idxmin()
            lowest_value = data.groupby('Year')['Value'].sum().min()
            return {
                "lowest_emissions_year": lowest_year,
                "lowest_emissions_value": lowest_value
            }
        
        # Helper function to calculate cumulative emissions for a country or region over a period.
        def cumulative_emissions(country=None, region=None, start_year=None, end_year=None):
            """
            Calculates cumulative emissions for a country or region over a specified period.

            Args:
            - country (str, optional): Country name.
            - region (str, optional): Region name.
            - start_year (int): Starting year.
            - end_year (int): Ending year.

            Returns:
            - dict: Cumulative emissions for the specified period.
            """
            data = df
            if country:
                data = df[(df['Country'] == country) & (df['Year'] >= start_year) & (df['Year'] <= end_year)]
            elif region:
                data = df[(df['World_Region'] == region) & (df['Year'] >= start_year) & (df['Year'] <= end_year)]
            else:
                data = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]
            cumulative_value = data['Value'].sum()
            return {
                "start_year": start_year,
                "end_year": end_year,
                "cumulative_emissions": cumulative_value
            }
        
        # Handle various analysis cases based on the requested action.
        # Depending on the action specified, the appropriate helper function is called to perform the analysis.
        if action == "country_emissions" and country and year:
            # If the action is 'country_emissions', and both 'country' and 'year' are provided,
            # call the 'get_country_emissions' function to fetch emissions for the specified country in the given year.
            result = get_country_emissions(country, year)
        
        elif action == "region_aggregation" and region:
            # If the action is 'region_aggregation' and a 'region' is provided,
            # call the 'aggregate_emissions_by_region' function to aggregate emissions for the specified region.
            # Optionally, filter the data by 'gas_type' if it's provided.
            result = aggregate_emissions_by_region(region, gas_type)
        
        elif action == "emissions_trend" and country:
            # If the action is 'emissions_trend' and a 'country' is provided,
            # call the 'emissions_trend_country' function to return the trend of emissions over time for that country.
            result = emissions_trend_country(country)
        
        elif action == "compare_countries" and country and region:
            # If the action is 'compare_countries', and both 'country' and 'region' are provided,
            # call the 'compare_countries' function to compare emissions between the specified country and region.
            # (Note: the region parameter might be used to compare with another country in this context.)
            result = compare_countries(country, region)
        
        elif action == "total_global_emissions":
            # If the action is 'total_global_emissions',
            # call the 'total_global_emissions' function to calculate and return total global emissions summed by year.
            result = total_global_emissions()
        
        elif action == "total_emissions_by_gas" and gas_type:
            # If the action is 'total_emissions_by_gas' and a 'gas_type' is provided,
            # call the 'total_emissions_by_gas' function to return total emissions for the specified gas type across all years.
            result = total_emissions_by_gas(gas_type)
        
        elif action == "emissions_by_region":
            # If the action is 'emissions_by_region',
            # call the 'emissions_by_region' function to return emissions data grouped by region and year.
            result = emissions_by_region()
        
        elif action == "top_n_countries_by_emissions" and year:
            # If the action is 'top_n_countries_by_emissions' and a 'year' is provided,
            # call the 'top_n_countries_by_emissions' function to return the top N countries by emissions for the specified year.
            # Optionally, the 'gas_type' parameter can be used to filter the data by a specific type of gas.
            result = top_n_countries_by_emissions(year, top_n, gas_type)
        
        elif action == "percentage_change_emissions" and start_year and end_year:
            # If the action is 'percentage_change_emissions' and both 'start_year' and 'end_year' are provided,
            # calculate the percentage change in emissions between the two specified years.
            # Depending on whether 'country' or 'region' is provided, it calculates the change for that specific country or region.
            if country:
                # If a 'country' is provided, calculate the percentage change in emissions for that country.
                result = percentage_change_emissions(country=country, start_year=start_year, end_year=end_year)
            elif region:
                # If a 'region' is provided instead, calculate the percentage change in emissions for that region.
                result = percentage_change_emissions(region=region, start_year=start_year, end_year=end_year)
            else:
                # If neither 'country' nor 'region' is provided, calculate the global percentage change in emissions.
                result = percentage_change_emissions(start_year=start_year, end_year=end_year)
        
        elif action == "highest_emissions_year":
            # If the action is 'highest_emissions_year',
            # call the 'highest_emissions_year' function to return the year with the highest emissions.
            # If a 'country' is provided, it returns the highest emissions year for that country.
            # If a 'region' is provided, it returns the highest emissions year for that region.
            # If neither is provided, it returns the global year with the highest emissions.
            if country:
                result = highest_emissions_year(country=country)
            elif region:
                result = highest_emissions_year(region=region)
            else:
                result = highest_emissions_year()
        
        elif action == "lowest_emissions_year":
            # If the action is 'lowest_emissions_year',
            # call the 'lowest_emissions_year' function to return the year with the lowest emissions.
            # If a 'country' is provided, it returns the lowest emissions year for that country.
            # If a 'region' is provided, it returns the lowest emissions year for that region.
            # If neither is provided, it returns the global year with the lowest emissions.
            if country:
                result = lowest_emissions_year(country=country)
            elif region:
                result = lowest_emissions_year(region=region)
            else:
                result = lowest_emissions_year()
        
        elif action == "cumulative_emissions" and start_year and end_year:
            # If the action is 'cumulative_emissions' and both 'start_year' and 'end_year' are provided,
            # call the 'cumulative_emissions' function to calculate the total emissions over the specified time range.
            # If a 'country' is provided, it returns the cumulative emissions for that country.
            # If a 'region' is provided, it returns the cumulative emissions for that region.
            # If neither is provided, it calculates global cumulative emissions over the time period.
            if country:
                result = cumulative_emissions(country=country, start_year=start_year, end_year=end_year)
            elif region:
                result = cumulative_emissions(region=region, start_year=start_year, end_year=end_year)
            else:
                result = cumulative_emissions(start_year=start_year, end_year=end_year)
        
        else:
            # If none of the above conditions are met, return an error message indicating that the action is invalid
            # or that the necessary parameters for the action are missing.
            result = f"Invalid action or missing parameters for action: {action}"

        # Return the final result as a JSON string.
        return result