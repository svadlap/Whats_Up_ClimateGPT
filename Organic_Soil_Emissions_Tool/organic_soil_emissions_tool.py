import inspect
import pandas as pd
from typing import Dict, Any, List
from custom_tools import SingleMessageCustomTool
from statsmodels.tsa.arima.model import ARIMA  

class OrganicSoilEmissionsTool(SingleMessageCustomTool):
    """
    Tool to analyze and retrieve emissions data for CO2 and N2O from organic soils, filtered by area, year range, 
    and other criteria. This tool provides comprehensive analytical capabilities to support climate-related research, 
    emissions tracking, and data-driven insights. It is equipped with a variety of functions including trend analysis, 
    comparisons, alert settings, and emissions forecasting. 

    Specifically, the tool supports the following actions:

    - **calculate_trends**: Analyzes trends in emissions over a specified time period for a given area. It determines whether emissions are increasing, decreasing, or stable based on historical data, providing an overview of emissions trajectories.

    - **get_summary_data**: Generates a summary of total CO2 and N2O emissions for all areas and years, with optional filters for specific areas and time ranges. This is useful for obtaining a quick overview of emissions data by region and emission type.

    - **compare_emissions**: Compares cumulative emissions across multiple areas over a specified date range. This function is useful for cross-regional comparisons and can help identify the highest-emitting regions over a given period.

    - **compare_emissions_with_conditions**: Allows for a detailed comparison of cumulative emissions across specified areas, with additional filtering based on emission type (CO2 or N2O), specific item type (e.g., cropland organic soils), source (e.g., FAO TIER 1), and unit (e.g., kt). This function provides a targeted view of emissions under specific conditions and is valuable for focused analyses on emissions sources and contexts. 
      
      Example usage:
      ```python
      result = await tool.run_impl(
          action="compare_emissions_with_conditions",
          areas=["Brazil", "India", "Russia"],
          element="Emissions (CO2)",
          item="Cropland organic soils",
          source="FAO TIER 1",
          unit="kt",
          start_year=2010,
          end_year=2021
      )
      ```
      Expected output is a dictionary with cumulative emissions data for each specified area, filtered by the conditions provided.

    - **list_highest_emissions**: Lists the areas with the highest emissions for a given element (CO2 or N2O) within a specified time frame. This can be useful for identifying top emitters by region or country.

    - **set_emission_alert**: Allows users to set alerts based on specific emissions thresholds. If emissions in a specified area exceed a given threshold, the tool will notify the user. This feature can help in monitoring critical emission levels.

    - **find_missing_data**: Identifies missing data points within the dataset for a specific area and emission type. It returns years where data is missing, which can assist in data quality assessments and help inform decisions on data interpolation or estimation.

    - **long_term_forecast**: Provides long-term forecasting of emissions using historical data. By employing statistical models, this function predicts future emissions over a user-specified number of years, which is valuable for future emissions projections and climate scenario analysis.

    - **analyze_correlation**: Calculates the correlation between CO2 and N2O emissions over a specified time period for a given area. This helps determine if there is a relationship between the two types of emissions, which may reveal insights into emissions drivers and co-occurrence patterns.

    - **average_annual_emissions**: Calculates the average annual emissions for a specified area and emission type (CO2 or N2O) over a defined time range. This can be useful for assessing the general emissions level in a region, averaged over multiple years.

    - **cumulative_emissions**: Computes the cumulative emissions for a specific area and emission type over a specified date range. This gives a total emissions figure for the given period, which is useful for historical emissions analysis and reporting.

    These functions collectively provide robust tools for analyzing emissions data, supporting climate impact studies, and assisting in data monitoring and forecasting for environmental management and policy-making.
    """


    def __init__(self):
        """
        Initialize the tool by loading the dataset from a specified file path 
        and filtering for CO2 and N2O data.
        """
        file_path = r'C:\Users\Saloni\Downloads\emissions-from-drained-organic-soils\emissions_organic-soils.xlsx'
        self.df = pd.read_excel(file_path)
        self.df = self.df[self.df['Element'].isin(['Emissions (CO2)', 'Emissions (N2O)'])]

    def get_name(self) -> str:
        return "organic_soil_emissions_tool"

    def get_description(self) -> str:
        return (
            "Analyze CO2 and N2O emissions from organic soils for specified areas, year ranges, and criteria. "
            "The tool provides functionality for calculating trends, comparing emissions, listing top emitters, "
            "setting alerts, identifying missing data, and forecasting future emissions."
        )
    def get_params_definition(self) -> Dict[str, Dict[str, Any]]:
        """Define the parameters accepted by the tool and their descriptions."""
        return {
            "action": {
                "param_type": "str",
                "description": (
                    "Specifies the action to perform. Supported actions: "
                    "'calculate_trends', 'get_summary_data', 'compare_emissions', "
                    "'list_highest_emissions', 'set_emission_alert', 'find_missing_data', "
                    "'long_term_forecast', 'analyze_correlation', 'average_annual_emissions', "
                    "'cumulative_emissions',"
                ),
                "required": True
            },
            "area": {
                "param_type": "str",
                "description": "Name of the country/area to analyze emissions.",
                "required": False
            },
            "start_year": {
                "param_type": "int",
                "description": "Starting year for the analysis, relevant for actions analyzing trends or comparisons.",
                "required": False
            },
            "end_year": {
                "param_type": "int",
                "description": "Ending year for the analysis, relevant for time-based actions.",
                "required": False
            },
            "element": {
                "param_type": "str",
                "description": "Type of emission element, such as 'Emissions (CO2)' or 'Emissions (N2O)'.",
                "required": False
            },
            "unit": {
                "param_type": "str",
                "description": "The unit of measurement, e.g., hectares for density calculations.",
                "required": False
            }
        }

    async def run_impl(self, action: str, **kwargs) -> Dict[str, Any]:
        actions = {
            "calculate_trends": self._calculate_trends,
            "get_summary_data": self._get_summary_data,
            "compare_emissions": self._compare_emissions,
            "list_highest_emissions": self._list_highest_emissions,
            "average_annual_emissions": self._average_annual_emissions,
            "cumulative_emissions": self._cumulative_emissions,
            "long_term_forecast": self._long_term_forecast,
            "analyze_correlation": self._analyze_correlation,
            "find_missing_data": self._find_missing_data,
            "compare_emissions_with_conditions": self._compare_emissions_with_conditions
        }
        
        if action in actions:
            func = actions[action]
            if inspect.iscoroutinefunction(func):
                return await func(**kwargs)
            else:
                return func(**kwargs)
        else:
            return {"status": "error", "message": "Invalid action specified."}


    async def _calculate_trends(self, area: str, start_year: int, end_year: int) -> Dict[str, Any]:
        """Calculate trends in emissions for CO2 and N2O over a specified time period for a country."""
        filtered_df = self._filter_data(area, start_year, end_year)
        trends = {}
        for element in ['Emissions (CO2)', 'Emissions (N2O)']:
            emissions_by_year = filtered_df[filtered_df['Element'] == element].groupby('Year')['Value'].sum()
            trend = "Increase" if emissions_by_year.iloc[-1] > emissions_by_year.iloc[0] else "Decrease" if emissions_by_year.iloc[-1] < emissions_by_year.iloc[0] else "Stable"
            trends[element] = {"yearly_emissions": emissions_by_year.to_dict(), "trend": trend}
        return {"status": "success", "trends": trends}

    def _filter_data(self, area: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Filter data by area and year range."""
        filtered_df = self.df[(self.df['Area'].str.lower() == area.lower()) & (self.df['Year'].between(start_year, end_year))]
        print(f"Filtered data for {area} from {start_year} to {end_year}:\n", filtered_df)  # Debug print
        return filtered_df

    def new_method(self, area, start_year, end_year):
        """Filter data by area and year range."""
        filtered_df = self.df[(self.df['Area'].str.lower() == area.lower()) & (self.df['Year'].between(start_year, end_year))]
        print(f"Filtered data for {area} from {start_year} to {end_year}:\n", filtered_df)  # Debug print
        return filtered_df


    def _get_summary_data(self, **kwargs) -> Dict[str, Any]:
        """Summarize total CO2 and N2O emissions for all areas and years, or filter by specific criteria."""
        
        area = kwargs.get('area')
        start_year = kwargs.get('start_year')
        end_year = kwargs.get('end_year')

        # Apply optional filters based on area and year range
        filtered_df = self.df.copy()
        if area:
            filtered_df = filtered_df[filtered_df['Area'].str.lower() == area.lower()]
        if start_year and end_year:
            filtered_df = filtered_df[filtered_df['Year'].between(start_year, end_year)]

        # Summarize emissions by type
        summary = filtered_df.groupby('Element')['Value'].sum().to_dict()
        return {"status": "success", "summary": summary}

    async def _compare_emissions(self, areas: List[str], start_year: int, end_year: int) -> Dict[str, Any]:
            """Compare emissions between specified countries over a specified time range."""
            comparison_data = {}
            for area in areas:
                filtered_df = self._filter_data(area, start_year, end_year)
                comparison_data[area] = filtered_df.groupby('Element')['Value'].sum().to_dict()
            return {"status": "success", "comparison_data": comparison_data}

    def _list_highest_emissions(self, element: str, start_year: int, end_year: int) -> Dict[str, Any]:
        """List the countries with the highest emissions of a given type in a specified time period."""
        # Filter data by year range and element
        filtered_df = self.df[
            (self.df['Year'] >= start_year) &
            (self.df['Year'] <= end_year) &
            (self.df['Element'] == element)
        ]
        
        # Check if there is data after filtering
        if filtered_df.empty:
            return {"status": "error", "message": f"No data available for {element} emissions from {start_year} to {end_year}."}
        
        # Sum emissions by area and sort to find the highest emitters
        highest_emissions = (
            filtered_df.groupby('Area')['Value']
            .sum()
            .sort_values(ascending=False)
            .to_dict()
        )
        
        return {
            "status": "success",
            "highest_emissions": highest_emissions,
            "element": element,
            "start_year": start_year,
            "end_year": end_year
        }


    def _set_emission_alert(self, area: str, element: str, threshold: float) -> Dict[str, Any]:
        """Set an alert if emissions in a specified country exceed a certain threshold."""
        area_data = self.df[(self.df['Area'].str.lower() == area.lower()) & (self.df['Element'] == element)]
        exceeded = area_data[area_data['Value'] > threshold]
        if not exceeded.empty:
            return {"status": "alert", "message": f"{element} emissions in {area} exceeded {threshold}."}
        return {"status": "success", "message": "No alert triggered."}

    def _find_missing_data(self, area: str, element: str) -> Dict[str, Any]:
        """
        Identify missing data points for a country for a specified emission type.
        
        Args:
        - area (str): The name of the country/area.
        - element (str): The emission type (e.g., 'Emissions (CO2)', 'Emissions (N2O)').
        
        Returns:
        - dict: Status of success and a list of missing years.
        """
        # Filter data by area and element
        area_data = self.df[(self.df['Area'].str.lower() == area.lower()) & (self.df['Element'] == element)]
        
        # Define the full range of years present in the dataset
        all_years = set(range(self.df['Year'].min(), self.df['Year'].max() + 1))
        
        # Gather the years recorded for the specified area and element
        recorded_years = set(area_data['Year'])
        
        # Calculate missing years by finding the difference
        missing_years = sorted(all_years - recorded_years)
        
        return {
            "status": "success",
            "area": area,
            "element": element,
            "missing_years": missing_years
        }

    async def _long_term_forecast(self, area: str, element: str, projection_years: int) -> Dict[str, Any]:
        """Forecast future emissions based on historical data using ARIMA."""
        area_data = self.df[(self.df['Area'].str.lower() == area.lower()) & (self.df['Element'] == element)]
        
        if area_data.empty:
            return {"status": "error", "message": f"No historical data for {element} in {area}."}
        
        # Convert 'Year' column to a datetime index for ARIMA compatibility
        area_data = area_data.set_index(pd.to_datetime(area_data['Year'], format='%Y'))

        # Ensure 'Value' column is numeric and ARIMA-compatible
        if area_data['Value'].sum() == 0:
            return {"status": "error", "message": f"All historical values are zero for {element} in {area}."}

        model = ARIMA(area_data['Value'], order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=projection_years)
        return {"status": "success", "forecast": forecast.tolist()}

    async def _analyze_correlation(self, area: str, start_year: int, end_year: int) -> Dict[str, Any]:
        """Calculate correlation between CO2 and N2O emissions over a given time period for an area."""
        filtered_df = self._filter_data(area, start_year, end_year)
        if filtered_df.empty:
            return {"status": "error", "message": "No data found for specified area and date range."}

        # Aggregate duplicate entries by summing their values for each year and element
        filtered_df = filtered_df.groupby(['Year', 'Element'])['Value'].sum().reset_index()
        
        # Pivot the data to have 'Year' as the index, 'Element' as columns, and 'Value' as values
        pivoted_df = filtered_df.pivot(index='Year', columns='Element', values='Value')
        
        # Check if both CO2 and N2O columns exist after pivoting
        if 'Emissions (CO2)' in pivoted_df.columns and 'Emissions (N2O)' in pivoted_df.columns:
            correlation = pivoted_df['Emissions (CO2)'].corr(pivoted_df['Emissions (N2O)'])
            return {"status": "success", "correlation": correlation}
        else:
            return {"status": "error", "message": "Insufficient data for correlation analysis."}

    def _filter_data(self, area: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Filter data by area and year range."""
        filtered_df = self.df[
            (self.df['Area'].str.lower() == area.lower()) &
            (self.df['Year'].between(start_year, end_year))
        ]
        return filtered_df

        
    async def _average_annual_emissions(self, area: str, element: str, start_year: int, end_year: int) -> Dict[str, Any]:
        """Calculate the average annual emissions for a specified area and emission type over a given time range."""
        # Filter data for the specified area, element, and year range
        filtered_df = self.df[
            (self.df['Area'].str.lower() == area.lower()) &
            (self.df['Element'] == element) &
            (self.df['Year'] >= start_year) &
            (self.df['Year'] <= end_year)
        ]
        
        # Check if there's data available for the given criteria
        if filtered_df.empty:
            return {"status": "error", "message": f"No data available for {element} emissions in {area} from {start_year} to {end_year}."}
        
        # Calculate the average emissions per year within the specified range
        avg_emissions = filtered_df['Value'].mean()
        
        return {
            "status": "success",
            "average_annual_emissions": avg_emissions,
            "area": area,
            "element": element,
            "start_year": start_year,
            "end_year": end_year
        }

            
    async def _cumulative_emissions(self, area: str, element: str, start_year: int, end_year: int) -> Dict[str, Any]:
        """Calculate cumulative emissions for a specified area and emission type over a date range."""
        # Filter data by area, element, and year range
        filtered_df = self.df[
            (self.df['Area'].str.lower() == area.lower()) &
            (self.df['Element'] == element) &
            (self.df['Year'] >= start_year) &
            (self.df['Year'] <= end_year)
        ]
        
        # Check if there is data available for the given criteria
        if filtered_df.empty:
            return {"status": "error", "message": f"No data available for {element} emissions in {area} from {start_year} to {end_year}."}
        
        # Calculate cumulative emissions and convert to Python int
        cumulative_emissions = int(filtered_df['Value'].sum())
        
        return {
            "status": "success",
            "cumulative_emissions": cumulative_emissions,
            "area": area,
            "element": element,
            "start_year": start_year,
            "end_year": end_year
        }
    
    async def _compare_emissions_with_conditions(self, areas: List[str], element: str, item: str, source: str, unit: str, start_year: int, end_year: int) -> Dict[str, Any]:
        """Compare cumulative emissions for specified countries with specific item types, years, source, and unit."""
        comparison_data = {}
        for area in areas:
            filtered_df = self.df[
                (self.df['Area'].str.lower() == area.lower()) &
                (self.df['Element'] == element) &
                (self.df['Item'] == item) &
                (self.df['Source'] == source) &
                (self.df['Unit'] == unit) &
                (self.df['Year'].between(start_year, end_year))
            ]
            cumulative_emissions = filtered_df['Value'].sum()
            comparison_data[area] = float(cumulative_emissions)  # Convert to float for JSON serialization
        
        return {
            "status": "success",
            "comparison_data": comparison_data,
            "element": element,
            "item": item,
            "source": source,
            "unit": unit,
            "start_year": start_year,
            "end_year": end_year
        }
