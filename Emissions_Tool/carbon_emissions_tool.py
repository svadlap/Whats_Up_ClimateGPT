# -*- coding: utf-8 -*-
"""
Created on Tue Sept 17 16:30:43 2024

Modified on Wed Oct 16 21:53:35 2024

@author: Vishay Paka
"""


import pandas as pd
from typing import Dict, Any, List
from custom_tools import SingleMessageCustomTool
from llama_stack_client.types.tool_param_definition_param import ToolParamDefinitionParam

# Load the carbon emissions data globally, allowing access across all instances
df = pd.read_csv('carbon-monitor-global-cleaned.csv')

class CarbonEmissionsTool(SingleMessageCustomTool):
    """
    Tool to retrieve carbon emissions data based on specified criteria such as country, date, and sector.
    
    This tool supports querying carbon emissions data for one or more countries, optionally filtering by
    a specific date and/or sector. It provides aggregated emissions data in metric tons of CO2 (MtCO2) per day.
    """

    def get_name(self) -> str:
        """Return the unique name of the tool used for invocation."""
        return "get_carbon_emissions"

    def get_description(self) -> str:
        """
        Provide a detailed description of the tool.
        
        This description informs the user that the tool can fetch carbon emissions data for given criteria.
        It can handle requests for multiple countries, optional filtering by a specific date in 'dd/mm/yyyy'
        format, and/or a particular sector (e.g., 'Transport', 'Energy'). If no date or sector is specified,
        the tool returns total emissions data across all dates and sectors for the specified countries.
        """
        return (
            "Retrieve carbon emissions data for one or more specified countries, "
            "optionally filtered by a specific date in 'dd/mm/yyyy' format and/or sector. "
            "The tool provides total daily carbon emissions measured in MtCO2 per day. "
            "If no date or sector is provided, it returns total emissions across all dates and sectors."
        )

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        """
        Define the parameters accepted by the tool and their descriptions.
        
        The tool accepts the following parameters:
        - country: Optional parameter specifying one or more countries separated by commas. If not provided, data across all countries will be aggregated.
        - date: Optional parameter specifying the date for the data, formatted as 'dd/mm/yyyy'.
        - sector: Optional parameter specifying the sector (e.g., 'Transport', 'Energy').
        """
        return {
            "country": ToolParamDefinitionParam(
                param_type="str",
                description=(
                    "The country (or list of countries separated by commas) for which to fetch carbon emissions data. "
                    "For example, 'India' or 'India, Brazil'. If not provided, data for all countries will be aggregated."
                ),
                required=False,
            ),
            "date": ToolParamDefinitionParam(
                param_type="str",
                description=(
                    "The specific date for which to get carbon emissions data, in 'dd/mm/yyyy' format. "
                    "If not provided, data across all dates will be aggregated."
                ),
                required=False,
            ),
            "sector": ToolParamDefinitionParam(
                param_type="str",
                description=(
                    "The sector for which to filter the carbon emissions data (e.g., 'Transport', 'Energy'). "
                    "If not provided, data across all sectors will be aggregated."
                ),
                required=False,
            ),
        }

    async def run_impl(self, country: str = None, date: str = None, sector: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Execute the tool's main logic to retrieve carbon emissions data.

        The tool fetches data for the specified country or countries, optionally filtering by date, date range, and sector.
        It returns the total daily carbon emissions in MtCO2 per day, or an error message if no data matches the criteria.

        Parameters:
        - country (str, optional): The country or list of countries for which to fetch the data, separated by commas.
                                   If not provided, data across all countries will be aggregated.
        - date (str, optional): The date for which to get data in 'dd/mm/yyyy' format. Default is None.
        - start_date (str, optional): The start date for aggregating data in 'dd/mm/yyyy' format. Default is None.
        - end_date (str, optional): The end date for aggregating data in 'dd/mm/yyyy' format. Default is None.
        - sector (str, optional): The sector to filter the data (e.g., 'Transport', 'Energy'). Default is None.

        Returns:
        - Dict[str, Any]: A dictionary containing the status of the request and the aggregated results.
        """
        # Convert the 'date' column in the DataFrame to datetime for accurate filtering
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')

        # Filter by countries if specified
        if country:
            country_list = [c.strip() for c in country.split(',')]
            # Validate if countries are in the dataset
            valid_countries = df['country'].unique()
            invalid_countries = [c for c in country_list if c not in valid_countries]

            if invalid_countries:
                return [
                    {
                        "country": ", ".join(invalid_countries),
                        "error": f"The specified country or countries ({', '.join(invalid_countries)}) "
                                 "are not present in the dataset."
                    }
                ]

            filtered_df = df[df['country'].isin(country_list)]
        else:
            # If no country is specified, use all data
            filtered_df = df.copy()

        # Handle specific date, start date, and end date filtering
        query_date = None
        if date:
            try:
                query_date = pd.to_datetime(date, format='%d/%m/%Y')
                filtered_df = filtered_df[filtered_df['date'] == query_date]
            except ValueError:
                return [
                    {
                        "country": "all",
                        "error": "Invalid date format. Please provide the date in 'dd/mm/yyyy' format."
                    }
                ]
        elif start_date and end_date:
            try:
                start = pd.to_datetime(start_date, format='%d/%m/%Y')
                end = pd.to_datetime(end_date, format='%d/%m/%Y')
                filtered_df = filtered_df[(filtered_df['date'] >= start) & (filtered_df['date'] <= end)]
            except ValueError:
                return [
                    {
                        "country": "all",
                        "error": "Invalid date range format. Please provide dates in 'dd/mm/yyyy' format."
                    }
                ]

        # If a sector is provided, validate and filter the DataFrame for that sector
        if sector:
            # Validate if the sector exists in the dataset
            valid_sectors = df['sector'].unique()
            if sector not in valid_sectors:
                return [
                    {
                        "sector": sector,
                        "error": f"The specified sector '{sector}' is not available in the dataset. "
                                 f"Please choose from the available sectors: {', '.join(valid_sectors)}."
                    }
                ]

            # Filter data for the valid sector
            filtered_df = filtered_df[filtered_df['sector'].str.contains(sector, case=False, na=False)]

            print(filtered_df)

        # Check if there is any matching data after applying the filters
        if not filtered_df.empty:
            # Aggregate the total emissions in MtCO2 per day
            total_emissions = filtered_df['MtCO2 per day'].sum()
            emissions_info = {
                "country": "all" if not country else ", ".join(country_list),
                "date": query_date.strftime('%d/%m/%Y') if query_date else "All Dates" if not (start_date and end_date) else f"From {start_date} to {end_date}",
                "sector": sector if sector else "All Sectors",
                "total_emissions": f"{total_emissions:.4f} MtCO2"
            }
            # Return the aggregated emissions information
            return emissions_info
        else:
            # If no data matches the criteria, return an error message
            return {
                "country": "all" if not country else ", ".join(country_list),
                "error": f"No emissions data available for {'all' if not country else ', '.join(country_list)} "
                         f"{'on ' + query_date.strftime('%d/%m/%Y') if query_date else ''} "
                         f"{'in the sector ' + sector if sector else ''}."
            }
