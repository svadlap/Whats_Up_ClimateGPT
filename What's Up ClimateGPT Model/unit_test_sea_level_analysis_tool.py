# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 14:23:36 2024

@author: Dontonio
"""

import unittest
from unittest.mock import patch
import pandas as pd
from sea_level_analysis_tool import SeaLevelAnalysisTool  # Replace with actual import path

# Load the actual dataset and extract a smaller subset for testing
full_data = pd.read_excel('Change_In_Mean_Sea_Level - climate_data_imf_org.xlsx')
full_data['Date'] = pd.to_datetime(full_data['Date'].str.lstrip('D'), errors='coerce')

# Define a subset as mock data for testing
mock_data = full_data[(full_data['Measure'].isin(['Adriatic Sea', 'Arabian Sea', 'Pacific Ocean', 'Atlantic Ocean'])) & 
                      (full_data['Date'].dt.year >= 2000) & (full_data['Date'].dt.year <= 2018)]

class TestSeaLevelAnalysisTool(unittest.TestCase):

    @patch('sea_level_analysis_tool.sea_level_data', mock_data)  # Patch global sea_level_data with mock_data
    def setUp(self):
        # Initialize the tool
        self.tool = SeaLevelAnalysisTool()

    def test_temporal_patterns_and_anomalies(self):
        result = self.tool.temporal_patterns_and_anomalies(region="Adriatic Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Region", result)
        self.assertIn("Anomalies", result)

    def test_compare_variability(self):
        result = self.tool.compare_variability()
        self.assertIsInstance(result, dict)
        self.assertTrue(len(result) > 0)

    def test_correlation_between_regions(self):
        result = self.tool.correlation_between_regions("Adriatic Sea", "Arabian Sea")
        self.assertIsInstance(result, (float, str))

    def test_trend_with_outliers(self):
        result = self.tool.trend_with_outliers(region="Adriatic Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Region", result)
        self.assertIn("Slope With Outliers", result)

    def test_seasonal_peaks_troughs(self):
        result = self.tool.seasonal_peaks_troughs(region="Adriatic Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Region", result)
        self.assertIn("Seasonal Peaks", result)

    def test_annual_rate_of_change(self):
        result = self.tool.annual_rate_of_change(region="Adriatic Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Region", result)
        self.assertIn("Annual Rate of Change", result)

    def test_positive_negative_ratio(self):
        result = self.tool.positive_negative_ratio(region="Adriatic Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Positive to Negative Ratio", result)

    def test_consistency_over_time(self):
        result = self.tool.consistency_over_time(region="Adriatic Sea")
        self.assertIsInstance(result, float)

    def test_decadal_shifts(self):
        result = self.tool.decadal_shifts(region="Adriatic Sea")
        self.assertIsInstance(result, dict)

    def test_rank_by_average_annual_change(self):
        result = self.tool.rank_by_average_annual_change()
        self.assertIsInstance(result, dict)

    def test_seasonal_consistency(self):
        result = self.tool.seasonal_consistency(region="Adriatic Sea")
        self.assertIsInstance(result, dict)

    def test_sea_level_hotspots(self):
        result = self.tool.sea_level_hotspots()
        self.assertIsInstance(result, dict)

    def test_trend_reversal_detection(self):
        result = self.tool.trend_reversal_detection(region="Adriatic Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Reversals", result)

    def test_acceleration_analysis(self):
        result = self.tool.acceleration_analysis(region="Adriatic Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Acceleration", result)

    def test_leading_lagging_indicators(self):
        result = self.tool.leading_lagging_indicators(region1="Adriatic Sea", region2="Arabian Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Lag between regions", result)

    def test_forecast_sea_level(self):
        result = self.tool.forecast_sea_level(region="Adriatic Sea", periods=5)
        self.assertIsInstance(result, dict)

    def test_monthly_vs_annual_fluctuations(self):
        result = self.tool.monthly_vs_annual_fluctuations(region="Adriatic Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Monthly Fluctuations", result)

    def test_extreme_event_frequency_duration(self):
        result = self.tool.extreme_event_frequency_duration(region="Adriatic Sea", threshold=2.5)
        self.assertIsInstance(result, dict)
        self.assertIn("Frequency", result)

    def test_dominant_trends(self):
        result = self.tool.dominant_trends(region="Adriatic Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Trend", result)

    def test_stabilization_events(self):
        result = self.tool.stabilization_events(region="Adriatic Sea", threshold=5)
        self.assertIsInstance(result, list)

    def test_seasonal_vs_non_seasonal_variation(self):
        result = self.tool.seasonal_vs_non_seasonal_variation(region="Adriatic Sea")
        self.assertIsInstance(result, dict)
        self.assertIn("Seasonal Variation", result)

    def test_peak_to_trough_analysis(self):
        result = self.tool.peak_to_trough_analysis(region="Adriatic Sea", period="YE")
        self.assertIsInstance(result, dict)

# Run the tests
if __name__ == "__main__":
    unittest.main()
