# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 11:32:34 2024

@author: Dontonio
"""

# Import necessary libraries
import pandas as pd  # For data manipulation and analysis
import numpy as np  # For numerical operations and calculations
from scipy.stats import zscore  # For calculating z-scores to detect anomalies
from statsmodels.tsa.seasonal import seasonal_decompose  # For time series decomposition
from statsmodels.tsa.arima.model import ARIMA  # For time series forecasting
from sklearn.linear_model import LinearRegression  # For trend analysis
from typing import Dict, Optional, Union  # For type annotations
import json  # For data serialization
from custom_tools import SingleMessageCustomTool  # Custom tool base class
from llama_stack_client.types.tool_param_definition_param import ToolParamDefinitionParam  # Custom parameter definitions

# Load dataset globally to use across functions
sea_level_data = pd.read_excel('Change_In_Mean_Sea_Level - climate_data_imf_org.xlsx')

# Convert 'Date' column to datetime format, removing any leading character ('D')
sea_level_data['Date'] = pd.to_datetime(sea_level_data['Date'].str.lstrip('D'), errors='coerce')

# Define SeaLevelAnalysisTool class inheriting from SingleMessageCustomTool
class SeaLevelAnalysisTool(SingleMessageCustomTool):
    """
    Tool for analyzing sea level change data based on regions and dates.
    Provides multiple methods for examining sea level data using time series analysis, trend detection, etc.
    """

    def get_name(self) -> str:
        # Return the name of the tool
        return "sea_level_analysis_tool"

    def get_description(self) -> str:
        # Return a description of the tool's purpose
        return "Perform analysis on sea level data."

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        # Define and return parameters for each function in the tool
        return {
            "action": ToolParamDefinitionParam(
                param_type="str",
                description="Type of analysis to perform, such as 'temporal_patterns', 'compare_variability', etc.",
                required=True,
            ),
            "region": ToolParamDefinitionParam(
                param_type="str",
                description="Region name for analysis (if applicable).",
                required=False,
            ),
            "region2": ToolParamDefinitionParam(
                param_type="str",
                description="Second region name for analysis (if applicable).",
                required=False,
            ),
            "threshold": ToolParamDefinitionParam(
                param_type="float",
                description="Threshold for identifying extreme events (if applicable).",
                required=False,
            ),
            "period": ToolParamDefinitionParam(
                param_type="str",
                description="Period for aggregation ('Y' for yearly, 'M' for monthly, etc.).",
                required=False,
            ),
        }

    async def run_impl(
        self,
        action: str,
        region: Optional[str] = None,
        region2: Optional[str] = None,
        threshold: Optional[float] = None,
        period: Optional[str] = 'Y',
    ) -> str:
        """
        Execute the chosen action based on input parameters.
        Each 'action' represents a different type of analysis or processing on sea level data.
        """
        # Check the 'action' and call the corresponding function
        if action == "temporal_patterns":
            result = self.temporal_patterns_and_anomalies(region)
        elif action == "compare_variability":
            result = self.compare_variability()
        elif action == "correlation_between_regions" and region and region2:
            result = self.correlation_between_regions(region, region2)
        elif action == "trend_with_outliers" and region:
            result = self.trend_with_outliers(region)
        elif action == "seasonal_peaks_troughs" and region:
            result = self.seasonal_peaks_troughs(region)
        elif action == "annual_rate_of_change" and region:
            result = self.annual_rate_of_change(region)
        elif action == "positive_negative_ratio" and region:
            result = self.positive_negative_ratio(region)
        elif action == "consistency_over_time" and region:
            result = self.consistency_over_time(region)
        elif action == "decadal_shifts" and region:
            result = self.decadal_shifts(region)
        elif action == "rank_by_average_annual_change":
            result = self.rank_by_average_annual_change()
        elif action == "seasonal_consistency" and region:
            result = self.seasonal_consistency(region)
        elif action == "sea_level_hotspots":
            result = self.sea_level_hotspots()
        elif action == "trend_reversal_detection" and region:
            result = self.trend_reversal_detection(region)
        elif action == "acceleration_analysis" and region:
            result = self.acceleration_analysis(region)
        elif action == "leading_lagging_indicators" and region and region2:
            result = self.leading_lagging_indicators(region, region2)
        elif action == "forecast_sea_level" and region:
            result = self.forecast_sea_level(region)
        elif action == "monthly_vs_annual_fluctuations" and region:
            result = self.monthly_vs_annual_fluctuations(region)
        elif action == "extreme_event_frequency_duration" and region:
            result = self.extreme_event_frequency_duration(region, threshold)
        elif action == "dominant_trends" and region:
            result = self.dominant_trends(region)
        elif action == "stabilization_events" and region:
            result = self.stabilization_events(region, threshold)
        elif action == "seasonal_vs_non_seasonal_variation" and region:
            result = self.seasonal_vs_non_seasonal_variation(region)
        elif action == "peak_to_trough_analysis" and region:
            result = self.peak_to_trough_analysis(region, period)
        else:
            result = "Invalid action or missing parameters."

        # Convert results to JSON format and return
        return json.dumps(self.convert_types(result), ensure_ascii=False)

    def convert_types(self, data):
        """
        Recursively convert data types to make them JSON-serializable.
        Converts DataFrame, Series, Timestamp, and numpy data types for JSON compatibility.
        """
        # Conversion logic for different data types
        if isinstance(data, list):
            return [self.convert_types(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.convert_types(value) for key, value in data.items()}
        elif isinstance(data, pd.DataFrame):
            return data.replace({pd.NaT: None}).to_dict(orient='records')
        elif isinstance(data, pd.Series):
            return data.replace({pd.NaT: None}).tolist()
        elif isinstance(data, (pd.Timestamp, pd.Timedelta)):
            return str(data) if pd.notna(data) else None
        elif isinstance(data, (np.int32, np.int64, np.float32, np.float64)):
            return data.item()
        elif data is pd.NaT:
            return None
        return data

    # Each of the following methods performs specific analysis on sea level data

    def temporal_patterns_and_anomalies(self, region: str) -> Dict:
        """
        Analyze and detect anomalies in sea level data for a specified region.
        Uses z-score to identify points deviating significantly from the mean.
        """
        region_data = sea_level_data[sea_level_data['Measure'] == region]
        anomalies = region_data[(np.abs(zscore(region_data['Value'])) > 2.5)]
        return {"Region": region, "Anomalies": anomalies.to_dict(orient="records")}

    def compare_variability(self) -> Dict:
        """
        Compare sea level variability across regions based on the standard deviation.
        Returns regions sorted by variability in descending order.
        """
        variability = sea_level_data.groupby('Measure')['Value'].std().sort_values(ascending=False)
        return variability.to_dict()

    def correlation_between_regions(self, region1: str, region2: str) -> Union[float, str]:
        """
        Calculate correlation between sea levels in two regions over overlapping dates.
        Checks for sufficient data points for meaningful correlation calculation.
        """
        data1 = sea_level_data[sea_level_data['Measure'] == region1].set_index('Date')['Value'].groupby(level=0).mean()
        data2 = sea_level_data[sea_level_data['Measure'] == region2].set_index('Date')['Value'].groupby(level=0).mean()
        
        combined_data = pd.DataFrame({'Region1': data1, 'Region2': data2}).dropna()
        num_points = combined_data.shape[0]
        if num_points < 2:
            return f"Insufficient overlapping data for correlation calculation: only {num_points} overlapping points found."
        
        correlation = combined_data['Region1'].corr(combined_data['Region2'])
        return correlation if pd.notna(correlation) else "Correlation could not be computed due to data limitations."

    def trend_with_outliers(self, region: str) -> Dict:
        """
        Calculate the slope (trend) of sea level values, both with and without outliers.
        Uses z-score to identify and remove outliers for trend comparison.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        slope_with_outliers = np.polyfit(data.index, data['Value'], 1)[0]
        data_no_outliers = data[(np.abs(zscore(data['Value'])) < 2.5)]
        slope_no_outliers = np.polyfit(data_no_outliers.index, data_no_outliers['Value'], 1)[0]
        return {"Region": region, "Slope With Outliers": slope_with_outliers, "Slope Without Outliers": slope_no_outliers}

    def seasonal_peaks_troughs(self, region: str) -> Dict:
        """
        Determine the months with peak and trough sea levels for a given region.
        Calculates average values by month to identify peak and trough periods.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        data['Month'] = data['Date'].dt.month
        monthly_avg = data.groupby('Month')['Value'].mean()
        return {"Region": region, "Seasonal Peaks": monthly_avg.idxmax(), "Troughs": monthly_avg.idxmin()}

    def annual_rate_of_change(self, region: str) -> Dict:
        """
        Calculate the annual rate of change in sea levels for a specified region.
        Uses linear regression on yearly averaged data to estimate rate of change.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        data['Year'] = data['Date'].dt.year
        yearly_avg = data.groupby('Year')['Value'].mean().reset_index()
        model = LinearRegression().fit(yearly_avg[['Year']], yearly_avg['Value'])
        return {"Region": region, "Annual Rate of Change": model.coef_[0]}

    def positive_negative_ratio(self, region: str) -> Dict:
        """
        Calculate the ratio of positive to negative sea level values for a given region.
        Useful for understanding the general direction of change in sea levels.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        positives = (data['Value'] > 0).sum()
        negatives = (data['Value'] < 0).sum()
        return {"Region": region, "Positive to Negative Ratio": positives / negatives}

    def consistency_over_time(self, region: str) -> float:
        """
        Calculate the standard deviation of yearly average sea levels to measure consistency.
        Higher values indicate greater variation in sea level over time.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        yearly_avg = data.groupby(data['Date'].dt.year)['Value'].mean()
        return yearly_avg.std()

    def decadal_shifts(self, region: str) -> Dict:
        """
        Analyze changes in sea levels over decades for a specified region.
        Groups data by decade and calculates the mean sea level for each.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        data['Decade'] = (data['Date'].dt.year // 10) * 10
        decadal_avg = data.groupby('Decade')['Value'].mean()
        return decadal_avg.to_dict()

    def rank_by_average_annual_change(self) -> Dict:
        """
        Rank regions by their average annual change in sea levels.
        Useful for identifying regions with the highest or lowest average changes over time.
        """
        data = sea_level_data.copy()
        data['Year'] = data['Date'].dt.year
        annual_change = data.groupby(['Measure', 'Year'])['Value'].mean().reset_index()
        avg_annual_change = annual_change.groupby('Measure')['Value'].mean().sort_values(ascending=False)
        return avg_annual_change.to_dict()

    def seasonal_consistency(self, region: str) -> Dict:
        """
        Analyze the consistency of seasonal sea level changes for a given region.
        Calculates standard deviation of seasonal changes to assess regularity.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        data['Season'] = data['Date'].dt.month % 12 // 3 + 1
        seasonal_change = data.groupby(['Season', data['Date'].dt.year])['Value'].mean().groupby('Season').std()
        return seasonal_change.to_dict()

    def sea_level_hotspots(self) -> Dict:
        """
        Identify regions with the highest average sea level changes, or 'hotspots.'
        Highlights top 5 regions with the greatest changes.
        """
        avg_changes = sea_level_data.groupby('Measure')['Value'].mean()
        hotspots = avg_changes.nlargest(5)
        return hotspots.to_dict()

    def trend_reversal_detection(self, region: str) -> Dict:
        """
        Detects points in the data where the trend in sea level changes direction.
        Useful for identifying turning points or trend shifts in the data.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        data['Trend'] = np.sign(data['Value'].diff())
        reversals = (data['Trend'].diff() != 0).sum()
        return {"Region": region, "Reversals": reversals}

    def acceleration_analysis(self, region: str) -> Dict:
        """
        Determine the acceleration of sea level changes over time for a region.
        Uses polynomial regression to estimate acceleration as a quadratic coefficient.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        data['Year'] = data['Date'].dt.year
        yearly_avg = data.groupby('Year')['Value'].mean()
        slope, accel = np.polyfit(range(len(yearly_avg)), yearly_avg, 2)[:2]
        return {"Region": region, "Acceleration": accel}

    def leading_lagging_indicators(self, region1: str, region2: str) -> Dict:
        """
        Identify leading or lagging relationships between two regions in sea levels.
        Calculates cross-correlation to find time lags.
        """
        data1 = sea_level_data[sea_level_data['Measure'] == region1].sort_values('Date')['Value']
        data2 = sea_level_data[sea_level_data['Measure'] == region2].sort_values('Date')['Value']
        cross_corr = np.correlate(data1, data2, mode="full")
        lag = np.argmax(cross_corr) - (len(data1) - 1)
        return {"Lag between regions": lag}

    def forecast_sea_level(self, region: str, periods: int = 12) -> Dict:
        """
        Forecast sea levels for a specified region using ARIMA model.
        Returns predictions for the next defined number of periods.
        """
        data = sea_level_data[sea_level_data['Measure'] == region].set_index('Date')
        model = ARIMA(data['Value'], order=(1,1,1)).fit()
        forecast = model.forecast(steps=periods)
        return forecast.to_dict()

    def monthly_vs_annual_fluctuations(self, region: str) -> Dict:
        """
        Compare monthly and annual fluctuations in sea levels for a region.
        Calculates standard deviation for both monthly and yearly data.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        data['Year'] = data['Date'].dt.year
        data['Month'] = data['Date'].dt.month
        monthly_change = data.groupby('Month')['Value'].std()
        annual_change = data.groupby('Year')['Value'].std()
        return {"Monthly Fluctuations": monthly_change.mean(), "Annual Fluctuations": annual_change.mean()}

    def extreme_event_frequency_duration(self, region: str, threshold: float = 2.5) -> Dict:
        """
        Calculate the frequency and duration of extreme sea level events for a region.
        Uses z-score to detect events exceeding the specified threshold.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        extreme_events = (np.abs(zscore(data['Value'])) > threshold)
        frequency = extreme_events.sum()
        duration = extreme_events.cumsum().max()  # assuming consecutive events
        return {"Frequency": frequency, "Max Duration": duration}

    def dominant_trends(self, region: str) -> Dict:
        """
        Identify the dominant trend in sea levels for a specified region (rising, falling, or stable).
        Uses linear regression to determine the trend direction.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        data['Year'] = data['Date'].dt.year
        yearly_avg = data.groupby('Year')['Value'].mean().reset_index()
        model = LinearRegression().fit(yearly_avg[['Year']], yearly_avg['Value'])
        trend = model.coef_[0]
        return {"Region": region, "Trend": "Rising" if trend > 0 else "Falling" if trend < 0 else "Stable"}

    def stabilization_events(self, region: str, threshold: float = 5) -> Dict:
        """
        Detect periods where sea levels remained within a specified range for each region.
        Uses a rolling window to identify periods with minimal fluctuations.
        """
        data = sea_level_data[sea_level_data['Measure'] == region].copy()
        data['Value Range'] = data['Value'].rolling(window=30, center=True).apply(lambda x: x.max() - x.min())
        stable_periods = data[data['Value Range'] < threshold]
        return stable_periods[['Date', 'Value']].to_dict(orient='records')

    def seasonal_vs_non_seasonal_variation(self, region: str) -> Dict:
        """
        Evaluate seasonal versus non-seasonal variation in sea levels for a region.
        Uses seasonal decomposition to assess the strength of seasonal components.
        """
        data = sea_level_data[sea_level_data['Measure'] == region]
        decomposition = seasonal_decompose(data.set_index('Date')['Value'], model='additive', period=12)
        seasonal_strength = np.var(decomposition.seasonal) / np.var(data['Value'])
        return {"Region": region, "Seasonal Variation": "Seasonal" if seasonal_strength > 0.5 else "Non-Seasonal"}

    def peak_to_trough_analysis(self, region: str, period: str = "YE") -> Dict:
        """
        Calculate peak-to-trough sea level range in a given period (yearly or monthly).
        Useful for understanding extreme fluctuations within specified time intervals.
        """
        data = sea_level_data[sea_level_data['Measure'] == region].set_index('Date')
        
        if period == "YE":
            period_range = data['Value'].resample('YE').apply(lambda x: x.max() - x.min())
        elif period == "M":
            period_range = data['Value'].resample('M').apply(lambda x: x.max() - x.min())
        else:
            raise ValueError("Unsupported period. Use 'YE' for yearly or 'M' for monthly.")
        
        period_range_dict = {str(date): value for date, value in period_range.items()}
        
        return period_range_dict
