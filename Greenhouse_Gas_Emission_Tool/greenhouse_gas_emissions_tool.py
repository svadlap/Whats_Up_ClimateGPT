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

class GreenhouseGasEmissionsTool(SingleMessageCustomTool):
    """
    Custom tool to perform analysis on greenhouse gas emissions data.

    Inherits from SingleMessageCustomTool to allow interaction with Llama models
    and provides methods to process emissions data based on different parameters.
    """

    def __init__(self):
        """Initialize the tool with no data loaded initially."""
        super().__init__()
        self.data = None  # Placeholder for the emissions data, to be loaded later.

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
        """
        return {
            # Parameter to specify the path of the emissions dataset (Excel file)
            "file_path": ToolParamDefinitionParam(
                param_type="str",
                description="Path to the greenhouse gas emissions dataset (Excel file).",
                required=True,
            ),
            # Parameter to specify the action/analysis to perform
            "action": ToolParamDefinitionParam(
                param_type="str",
                description="Type of analysis to perform: 'country_emissions', 'region_aggregation', etc.",
                required=True,
            ),
            # Optional parameter to specify a country for analysis
            "country": ToolParamDefinitionParam(
                param_type="str",
                description="Country name for analysis (if applicable).",
                required=False,
            ),
            # Optional parameter to specify a region for aggregation
            "region": ToolParamDefinitionParam(
                param_type="str",
                description="Region name for analysis (if applicable).",
                required=False,
            ),
            # Optional parameter to filter by a specific year
            "year": ToolParamDefinitionParam(
                param_type="int",
                description="Year for filtering data (if applicable).",
                required=False,
            ),
            # Optional parameter to filter by a specific type of gas (CO2, CH4, etc.)
            "gas_type": ToolParamDefinitionParam(
                param_type="str",
                description="Filter by specific gas type (if applicable).",
                required=False,
            ),
        }

    def _load_data(self, file_path: str):
        """
        Internal method to load and clean the dataset.
        - Reads the Excel file from the specified path.
        - Cleans the data by removing missing values and converting the 'Year' column to integers.
        """
        self.data = pd.read_excel(file_path)  # Load the data from an Excel file.
        self.data.dropna(inplace=True)  # Drop rows with missing values to clean the data.
        self.data['Year'] = self.data['Year'].astype(int)  # Ensure the 'Year' column is of integer type.

    async def run_impl(self, file_path: str, action: str, country: str = None, region: str = None, year: int = None, gas_type: str = None, start_year: int = None, end_year: int = None, n: int = 10):
        """
        Main function to execute the requested analysis based on the provided action.
        This method orchestrates various sub-functions based on the analysis type.
        
        Parameters:
        - file_path: Path to the emissions data file.
        - action: The type of analysis requested ('country_emissions', 'region_aggregation', etc.).
        - country: (Optional) Name of the country for country-specific analysis.
        - region: (Optional) Name of the region for region-based analysis.
        - year: (Optional) Year for filtering data.
        - gas_type: (Optional) Gas type filter (e.g., CO2, CH4).
        - start_year, end_year: (Optional) Range of years for time series analysis.
        - n: (Optional) Number of top countries to return (used in some analyses).
        """
        self._load_data(file_path)  # Load the emissions dataset before performing analysis.
        
        # Helper function to get emissions for a specific country and year.
        def get_country_emissions(country, year):
            """
            Fetches emissions data for a given country in a specific year.
        
            Args:
            - country (str): The name of the country.
            - year (int): The year for which to fetch the emissions.
        
            Returns:
            - dict: A dictionary containing the country, year, and emissions value.
                    If no data is available, it returns a message indicating that.
            """
            # Filter the dataset for the specified country and year.
            result = self.data[(self.data['Country'] == country) & (self.data['Year'] == year)]
            
            # If the filtered result is not empty, convert it to a dictionary.
            if not result.empty:
                return result[['Country', 'Year', 'Value']].to_dict(orient='records')
            else:
                # If no data is available, return an appropriate message.
                return f"No data available for {country} in {year}"
        
        
        # Helper function to aggregate emissions by region and optionally filter by gas type.
        def aggregate_emissions_by_region(region, gas_type=None):
            """
            Aggregates emissions data for a specific region over all years,
            optionally filtering by gas type.
        
            Args:
            - region (str): The name of the region.
            - gas_type (str, optional): The type of greenhouse gas to filter by (e.g., CO2, CH4).
        
            Returns:
            - dict: A dictionary containing the total emissions per year for the region,
                    optionally filtered by gas type.
            """
            # Filter the dataset for the specified region.
            filtered_data = self.data[self.data['World_Region'] == region]
            
            # If a specific gas type is provided, further filter the data by that gas type.
            if gas_type:
                filtered_data = filtered_data[filtered_data['Substance'] == gas_type]
            
            # Group the filtered data by year and sum the emissions values.
            # Convert the grouped result to a dictionary.
            return filtered_data.groupby('Year')['Value'].sum().reset_index().to_dict(orient='records')
        
        
        # Helper function to get the emissions trend over time for a specific country.
        def emissions_trend_country(country):
            """
            Retrieves the trend of emissions over time for a given country.
        
            Args:
            - country (str): The name of the country.
        
            Returns:
            - dict: A dictionary containing the emissions per year for the specified country.
            """
            # Filter the dataset for the specified country and group by year to calculate total emissions per year.
            trend = self.data[self.data['Country'] == country].groupby('Year')['Value'].sum().reset_index()
            
            # Convert the result to a dictionary.
            return trend.to_dict(orient='records')
        
        
        # Helper function to compare emissions between two countries.
        def compare_countries(country1, country2):
            """
            Compares emissions between two countries across all available years.
        
            Args:
            - country1 (str): The first country for comparison.
            - country2 (str): The second country for comparison.
        
            Returns:
            - dict: A dictionary containing emissions data for both countries side-by-side.
            """
            # Filter the dataset for each country and group by year to calculate total emissions.
            country1_data = self.data[self.data['Country'] == country1].groupby('Year')['Value'].sum().reset_index()
            country2_data = self.data[self.data['Country'] == country2].groupby('Year')['Value'].sum().reset_index()
            
            # Merge the two datasets on the 'Year' column to allow side-by-side comparison.
            comparison = pd.merge(country1_data, country2_data, on='Year', suffixes=(f'_{country1}', f'_{country2}'))
            
            # Convert the merged result to a dictionary.
            return comparison.to_dict(orient='records')
        
        
        # Helper function to calculate total global emissions across all years.
        def total_global_emissions():
            """
            Calculates the total global greenhouse gas emissions across all years.
        
            Returns:
            - dict: A dictionary containing the total emissions per year globally.
            """
            # Group the dataset by year and sum the emissions values for each year.
            global_emissions = self.data.groupby('Year')['Value'].sum().reset_index()
            
            # Convert the result to a dictionary.
            return global_emissions.to_dict(orient='records')
        
        
        # Helper function to calculate total emissions for a specific gas type.
        def total_emissions_by_gas(gas_type):
            """
            Calculates the total emissions for a specific gas type (e.g., CO2, CH4) across all years.
        
            Args:
            - gas_type (str): The type of greenhouse gas.
        
            Returns:
            - dict: A dictionary containing the total emissions per year for the specified gas type.
            """
            # Filter the dataset for the specified gas type.
            filtered_data = self.data[self.data['Substance'] == gas_type]
            
            # Group the filtered data by year and sum the emissions values.
            total_emissions = filtered_data.groupby('Year')['Value'].sum().reset_index()
            
            # Convert the result to a dictionary.
            return total_emissions.to_dict(orient='records')
        
        
        # Helper function to get emissions data by region and year.
        def emissions_by_region():
            """
            Retrieves total emissions data grouped by region and year.
        
            Returns:
            - dict: A dictionary containing emissions data for each region by year.
            """
            # Group the dataset by region and year, and sum the emissions values.
            emissions = self.data.groupby(['World_Region', 'Year'])['Value'].sum().reset_index()
            
            # Convert the result to a dictionary.
            return emissions.to_dict(orient='records')
        
        
        # Helper function to get the top N countries by emissions for a specific year.
        def top_n_countries_by_emissions(year, n=10, gas_type=None):
            """
            Retrieves the top N countries by emissions for a given year, optionally filtering by gas type.
        
            Args:
            - year (int): The year for which to fetch the top N countries.
            - n (int): The number of top countries to retrieve (default is 10).
            - gas_type (str, optional): The type of greenhouse gas to filter by.
        
            Returns:
            - dict: A dictionary containing the top N countries and their emissions for the specified year.
            """
            # Filter the dataset for the specified year.
            filtered_data = self.data[self.data['Year'] == year]
            
            # If a specific gas type is provided, further filter the data by that gas type.
            if gas_type:
                filtered_data = filtered_data[filtered_data['Substance'] == gas_type]
            
            # Group the data by country, sum the emissions values, and get the top N countries with the largest emissions.
            top_countries = filtered_data.groupby('Country')['Value'].sum().nlargest(n).reset_index()
            
            # Convert the result to a dictionary.
            return top_countries.to_dict(orient='records')
        
        
        # Helper function to calculate the percentage change in emissions between two years for a country or region.
        def percentage_change_emissions(country=None, region=None, start_year=None, end_year=None):
            """
            Calculates the percentage change in emissions between two specified years for a country or region.
        
            Args:
            - country (str, optional): The country to calculate the change for.
            - region (str, optional): The region to calculate the change for.
            - start_year (int): The starting year for the calculation.
            - end_year (int): The ending year for the calculation.
        
            Returns:
            - dict: A dictionary containing the percentage change in emissions between the two years.
            """
            # Filter the dataset based on whether a country or region is specified, and for the two selected years.
            if country:
                data = self.data[(self.data['Country'] == country) & (self.data['Year'].isin([start_year, end_year]))]
            elif region:
                data = self.data[(self.data['World_Region'] == region) & (self.data['Year'].isin([start_year, end_year]))]
            else:
                data = self.data[self.data['Year'].isin([start_year, end_year])]
        
            # Group the filtered data by year and sum the emissions values.
            emissions_by_year = data.groupby('Year')['Value'].sum().reset_index()
        
            # Ensure that data for both years is available before calculating the percentage change.
            if emissions_by_year.shape[0] == 2:
                start_value = emissions_by_year[emissions_by_year['Year'] == start_year]['Value'].values[0]
                end_value = emissions_by_year[emissions_by_year['Year'] == end_year]['Value'].values[0]
                # Calculate the percentage change: ((end - start) / start) * 100.
                percentage_change = ((end_value - start_value) / start_value) * 100
                return {'start_year': start_year, 'end_year': end_year, 'percentage_change': percentage_change}
            else:
                # If data for one of the years is missing, return an appropriate message.
                return "Data not available for the specified years."
        
        
        # Helper function to find the year with the highest emissions for a country or region.
        def highest_emissions_year(country=None, region=None):
            """
            Finds the year with the highest emissions for a given country, region, or globally.
        
            Args:
            - country (str, optional): The country to find the highest emissions year for.
            - region (str, optional): The region to find the highest emissions year for.
        
            Returns:
            - dict: A dictionary containing the year and the highest emissions value.
            """
            # Filter the dataset based on whether a country or region is specified.
            if country:
                data = self.data[self.data['Country'] == country]
            elif region:
                data = self.data[self.data['World_Region'] == region]
            else:
                data = self.data
        
            # Group the filtered data by year, sum the emissions values, and find the year with the highest emissions.
            highest_year = data.groupby('Year')['Value'].sum().idxmax()
            highest_value = data.groupby('Year')['Value'].sum().max()
            
            # Return the year and the corresponding highest emissions value.
            return {'year': highest_year, 'highest_emissions': highest_value}
        
        
        # Helper function to find the year with the lowest emissions for a country or region.
        def lowest_emissions_year(country=None, region=None):
            """
            Finds the year with the lowest emissions for a given country, region, or globally.
        
            Args:
            - country (str, optional): The country to find the lowest emissions year for.
            - region (str, optional): The region to find the lowest emissions year for.
        
            Returns:
            - dict: A dictionary containing the year and the lowest emissions value.
            """
            # Filter the dataset based on whether a country or region is specified.
            if country:
                data = self.data[self.data['Country'] == country]
            elif region:
                data = self.data[self.data['World_Region'] == region]
            else:
                data = self.data
        
            # Group the filtered data by year, sum the emissions values, and find the year with the lowest emissions.
            lowest_year = data.groupby('Year')['Value'].sum().idxmin()
            lowest_value = data.groupby('Year')['Value'].sum().min()
            
            # Return the year and the corresponding lowest emissions value.
            return {'year': lowest_year, 'lowest_emissions': lowest_value}
        
        
        # Helper function to calculate cumulative emissions for a specific country or region over a time period.
        def cumulative_emissions(country=None, region=None, start_year=None, end_year=None):
            """
            Calculates the cumulative emissions for a country or region between two specified years.
        
            Args:
            - country (str, optional): The country to calculate the cumulative emissions for.
            - region (str, optional): The region to calculate the cumulative emissions for.
            - start_year (int): The starting year of the period.
            - end_year (int): The ending year of the period.
        
            Returns:
            - dict: A dictionary containing the cumulative emissions over the specified period.
            """
            # Filter the dataset based on whether a country or region is specified, and for the specified time range.
            if country:
                data = self.data[(self.data['Country'] == country) & (self.data['Year'] >= start_year) & (self.data['Year'] <= end_year)]
            elif region:
                data = self.data[(self.data['World_Region'] == region) & (self.data['Year'] >= start_year) & (self.data['Year'] <= end_year)]
            else:
                data = self.data[(self.data['Year'] >= start_year) & (self.data['Year'] <= end_year)]
        
            # Sum the emissions values over the specified time range.
            cumulative_value = data['Value'].sum()
        
            # Return the cumulative emissions for the period.
            return {'start_year': start_year, 'end_year': end_year, 'cumulative_emissions': cumulative_value}
        
        
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
            result = top_n_countries_by_emissions(year, n, gas_type)
        
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
        return json.dumps(result, ensure_ascii=False)