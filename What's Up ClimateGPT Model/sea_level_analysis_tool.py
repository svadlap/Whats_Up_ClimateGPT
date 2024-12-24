# -*- coding: utf-8 -*-
"""
Sea Level Analysis Tool

Created on Fri Nov 1, 2024

@author: Dontonio
"""

import pandas as pd
import numpy as np
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression
from typing import Dict, Optional, Any
from custom_tools import SingleMessageCustomTool
from llama_stack_client.types.tool_param_definition_param import ToolParamDefinitionParam

# Load the dataset
sea_level_data = pd.read_excel('Change_In_Mean_Sea_Level - climate_data_imf_org.xlsx')

# Convert 'Date' column to datetime format, removing any leading character ('D')
sea_level_data['Date'] = pd.to_datetime(sea_level_data['Date'].str.lstrip('D'), errors='coerce')


class SeaLevelAnalysisTool(SingleMessageCustomTool):
    """
    Tool for analyzing sea level change data based on regions and dates.
    Provides multiple methods for examining sea level data using time series analysis, trend detection, etc.
    """

    def get_name(self) -> str:
        return "sea_level_analysis_tool"

    def get_description(self) -> str:
        return (
            "Analyze sea level data based on regions and time. Perform anomaly detection, variability comparisons, "
            "trend analysis, seasonal analysis, and more."
        )

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
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
        }

    async def run_impl(
        self,
        action: str,
        region: Optional[str] = None,
        region2: Optional[str] = None,
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        if action == "temporal_patterns":
            return self.temporal_patterns_and_anomalies(region)
        elif action == "compare_variability":
            return self.compare_variability()
        elif action == "correlation_between_regions" and region and region2:
            return self.correlation_between_regions(region, region2)
        elif action == "trend_with_outliers" and region:
            return self.trend_with_outliers(region)
        elif action == "seasonal_peaks_troughs" and region:
            return self.seasonal_peaks_troughs(region)
        else:
            return {"error": "Invalid action or missing parameters."}

    # Helper to convert DataFrame results into JSON-friendly formats
    def convert_to_dict(self, data: pd.DataFrame) -> Dict:
        return data.replace({np.nan: None}).to_dict(orient="records")

    def temporal_patterns_and_anomalies(self, region: str) -> Dict[str, Any]:
        region_data = sea_level_data[sea_level_data['Measure'] == region]
        if region_data.empty:
            return {"error": f"No data available for region '{region}'"}

        anomalies = region_data[(np.abs(zscore(region_data['Value'])) > 2.5)]
        return {
            "action": "temporal_patterns",
            "region": region,
            "anomalies": self.convert_to_dict(anomalies),
            "summary": {
                "total_anomalies": len(anomalies),
                "average_anomaly_value": anomalies['Value'].mean() if not anomalies.empty else None,
            },
        }

    def compare_variability(self) -> Dict[str, Any]:
        variability = sea_level_data.groupby('Measure')['Value'].std().sort_values(ascending=False)
        if variability.empty:
            return {"error": "No data available to compute variability."}

        return {
            "action": "compare_variability",
            "variability": variability.to_dict(),
            "summary": {
                "highest_variability_region": variability.idxmax(),
                "lowest_variability_region": variability.idxmin(),
            },
        }

    def correlation_between_regions(self, region1: str, region2: str) -> Dict[str, Any]:
        data1 = sea_level_data[sea_level_data['Measure'] == region1].set_index('Date')['Value']
        data2 = sea_level_data[sea_level_data['Measure'] == region2].set_index('Date')['Value']

        if data1.empty or data2.empty:
            return {"error": f"Data unavailable for region(s): {region1}, {region2}"}

        combined_data = pd.DataFrame({'Region1': data1, 'Region2': data2}).dropna()
        if combined_data.shape[0] < 2:
            return {"error": "Insufficient overlapping data for correlation calculation."}

        correlation = combined_data['Region1'].corr(combined_data['Region2'])
        return {
            "action": "correlation_between_regions",
            "region1": region1,
            "region2": region2,
            "correlation_coefficient": float(correlation),
            "summary": {
                "overlapping_data_points": combined_data.shape[0],
            },
        }

    def trend_with_outliers(self, region: str) -> Dict[str, Any]:
        region_data = sea_level_data[sea_level_data['Measure'] == region]
        if region_data.empty:
            return {"error": f"No data available for region '{region}'"}

        slope_with_outliers = np.polyfit(range(len(region_data)), region_data['Value'], 1)[0]
        filtered_data = region_data[(np.abs(zscore(region_data['Value'])) < 2.5)]
        slope_without_outliers = np.polyfit(range(len(filtered_data)), filtered_data['Value'], 1)[0]

        return {
            "action": "trend_with_outliers",
            "region": region,
            "trend_analysis": {
                "slope_with_outliers": float(slope_with_outliers),
                "slope_without_outliers": float(slope_without_outliers),
            },
            "summary": {
                "total_data_points": len(region_data),
                "filtered_data_points": len(filtered_data),
            },
        }

    def seasonal_peaks_troughs(self, region: str) -> Dict[str, Any]:
        region_data = sea_level_data[sea_level_data['Measure'] == region]
        if region_data.empty:
            return {"error": f"No data available for region '{region}'"}

        region_data['Month'] = region_data['Date'].dt.month
        monthly_avg = region_data.groupby('Month')['Value'].mean()

        return {
            "action": "seasonal_peaks_troughs",
            "region": region,
            "seasonal_analysis": {
                "peak_month": int(monthly_avg.idxmax()),
                "trough_month": int(monthly_avg.idxmin()),
                "monthly_averages": {int(k): float(v) for k, v in monthly_avg.items()},
            },
        }
