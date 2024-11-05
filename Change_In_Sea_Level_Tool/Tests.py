# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 11:37:44 2024

@author: Dontonio
"""

import nest_asyncio
nest_asyncio.apply()

import pandas as pd
import json
import asyncio
from sea_level_analysis_tool import SeaLevelAnalysisTool  # assuming this is the file name

# Initialize the tool
tool = SeaLevelAnalysisTool()  # assuming sea_level_data is already loaded in the tool

# Define a function to check results for each test case
def print_test_result(description, result):
    print(f"\n{description}")
    print(json.dumps(result, indent=2))

# Define an async function to call each method
async def main():
    # Test cases for each function
    
    # 1. Temporal Patterns and Anomalies
    result = await tool.run_impl(action="temporal_patterns", region="Adriatic Sea")
    print_test_result("Temporal patterns and anomalies for Adriatic Sea:", json.loads(result))
    
    # 2. Comparative Analysis of Variability
    result = await tool.run_impl(action="compare_variability")
    print_test_result("Comparative analysis of variability across regions:", json.loads(result))
    
    # 3. Correlation Between Neighboring Regions
    result = await tool.run_impl(action="correlation_between_regions", region="Adriatic Sea", region2="Arabian Sea")
    print_test_result("Correlation between Adriatic Sea and Arabian Sea:", json.loads(result))
    
    # 4. Impact of Extreme Events on Trend
    result = await tool.run_impl(action="trend_with_outliers", region="Adriatic Sea")
    print_test_result("Impact of extreme events on trend for Adriatic Sea:", json.loads(result))
    
    # 5. Seasonal Peaks and Troughs
    result = await tool.run_impl(action="seasonal_peaks_troughs", region="Adriatic Sea")
    print_test_result("Seasonal peaks and troughs for Adriatic Sea:", json.loads(result))
    
    # 6. Annual Rate of Change
    result = await tool.run_impl(action="annual_rate_of_change", region="Adriatic Sea")
    print_test_result("Annual rate of change for Adriatic Sea:", json.loads(result))
    
    # 7. Positive vs. Negative Changes
    result = await tool.run_impl(action="positive_negative_ratio", region="Adriatic Sea")
    print_test_result("Positive vs. negative changes for Adriatic Sea:", json.loads(result))
    
    # 8. Consistency Over Time
    result = await tool.run_impl(action="consistency_over_time", region="Adriatic Sea")
    print_test_result("Consistency over time for Adriatic Sea:", json.loads(result))
    
    # 9. Decadal Shifts
    result = await tool.run_impl(action="decadal_shifts", region="Adriatic Sea")
    print_test_result("Decadal shifts for Adriatic Sea:", json.loads(result))
    
    # 10. Rank by Average Annual Change
    result = await tool.run_impl(action="rank_by_average_annual_change")
    print_test_result("Ranking by average annual change:", json.loads(result))
    
    # 11. Seasonal Consistency Year-to-Year
    result = await tool.run_impl(action="seasonal_consistency", region="Adriatic Sea")
    print_test_result("Seasonal consistency year-to-year for Adriatic Sea:", json.loads(result))
    
    # 12. Identification of Sea Level Hotspots
    result = await tool.run_impl(action="sea_level_hotspots")
    print_test_result("Identification of sea level hotspots:", json.loads(result))
    
    # 13. Trend Reversal Detection
    result = await tool.run_impl(action="trend_reversal_detection", region="Adriatic Sea")
    print_test_result("Trend reversal detection for Adriatic Sea:", json.loads(result))
    
    # 14. Acceleration Analysis
    result = await tool.run_impl(action="acceleration_analysis", region="Adriatic Sea")
    print_test_result("Acceleration analysis for Adriatic Sea:", json.loads(result))
    
    # 15. Leading and Lagging Indicators
    result = await tool.run_impl(action="leading_lagging_indicators", region="Adriatic Sea", region2="Arabian Sea")
    print_test_result("Leading and lagging indicators between Adriatic Sea and Arabian Sea:", json.loads(result))
    
    # 16. Forecasting with ARIMA
    result = await tool.run_impl(action="forecast_sea_level", region="Adriatic Sea")
    print_test_result("Forecasting sea level for Adriatic Sea:", json.loads(result))
    
    # 17. Monthly vs. Annual Rate of Change
    result = await tool.run_impl(action="monthly_vs_annual_fluctuations", region="Adriatic Sea")
    print_test_result("Monthly vs. annual rate of change for Adriatic Sea:", json.loads(result))
    
    # 18. Frequency and Duration of Extreme Events
    result = await tool.run_impl(action="extreme_event_frequency_duration", region="Adriatic Sea", threshold=2.5)
    print_test_result("Frequency and duration of extreme events for Adriatic Sea:", json.loads(result))
    
    # 19. Dominant Trends for Rising vs. Falling Sea Levels by Region
    result = await tool.run_impl(action="dominant_trends", region="Adriatic Sea")
    print_test_result("Dominant trends for Adriatic Sea:", json.loads(result))
    
    # 20. Long-Term Stabilization Events
    result = await tool.run_impl(action="stabilization_events", region="Adriatic Sea", threshold=100)
    print_test_result("Long-term stabilization events for Adriatic Sea:", json.loads(result))
    
    # 21. Seasonal vs. Non-Seasonal Variation Classification
    result = await tool.run_impl(action="seasonal_vs_non_seasonal_variation", region="Adriatic Sea")
    print_test_result("Seasonal vs. non-seasonal variation classification for Adriatic Sea:", json.loads(result))
    
    # 22. Peak-to-Trough Analysis
    result = await tool.run_impl(action="peak_to_trough_analysis", region="Adriatic Sea", period="YE")
    print_test_result("Peak-to-trough analysis for Adriatic Sea:", json.loads(result))
    

# Run the async main function
asyncio.run(main())
