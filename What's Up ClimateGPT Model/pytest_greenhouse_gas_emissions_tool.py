# -*- coding: utf-8 -*-
"""
Test file for GreenhouseGasEmissionsTool

Created on: Wed Nov 15, 2024

Description: Pytest file for testing GreenhouseGasEmissionsTool

@author: Vishay Paka
"""

import pytest
import pandas as pd
from greenhouse_gas_emissions_tool import GreenhouseGasEmissionsTool

# Mock data for testing
mock_data = {
    'Country': ['Sao Tome and Principe', 'Suriname', 'United States', 'Germany', 'Sao Tome and Principe', 'Suriname', 'United States', 'Germany'],
    'Year': [2002, 2005, 2010, 2015, 2020, 2020, 2020, 2020],
    'World_Region': ['Western Africa', 'South America (Other)', 'North America', 'Europe', 'Western Africa', 'South America (Other)', 'North America', 'Europe'],
    'Substance': ['CO2', 'CH4', 'N2O', 'CO2', 'CH4', 'N2O', 'CO2', 'CO2'],
    'Value': [202.52, 237.81, 278.46, 280.76, 2412.99, 2700.93, 1938.79, 1594.00],
    'Unit': ['kt', 'kt', 'kt', 'kt', 'kt', 'kt', 'kt', 'kt']  # Add units for each row
}

# Create a DataFrame from the mock data
mock_df = pd.DataFrame(mock_data)

# Patch the global DataFrame in the GreenhouseGasEmissionsTool module
@pytest.fixture(autouse=True)
def patch_df(monkeypatch):
    monkeypatch.setattr("greenhouse_gas_emissions_tool.df", mock_df)

# Initialize the tool
ghg_tool = GreenhouseGasEmissionsTool()

# Test cases for the GreenhouseGasEmissionsTool
def test_get_name():
    """Test the get_name method"""
    assert ghg_tool.get_name() == "greenhouse_gas_emissions_tool"

def test_get_description():
    """Test the get_description method"""
    description = ghg_tool.get_description()
    assert "Perform analysis on greenhouse gas emissions data" in description

def test_get_params_definition():
    """Test the get_params_definition method"""
    params = ghg_tool.get_params_definition()
    assert "action" in params
    assert "country" in params
    assert "region" in params
    assert "year" in params
    assert "gas_type" in params

@pytest.mark.asyncio
async def test_run_impl_country_emissions_valid():
    """Test run_impl for a valid country and year with conversions and aggregation"""
    result = await ghg_tool.run_impl(action="country_emissions", country="United States", year=2010)
    assert result['country'] == "United States"
    assert result['year'] == 2010
    assert result['unit'] == "kt"
    assert result['emissions_by_substance'] == {"N2O": 278.46}  # Based on mock data
    assert result['total_emissions'] == 278.46  # Sum of converted values for United States in 2010

@pytest.mark.asyncio
async def test_run_impl_country_emissions_no_data():
    """Test run_impl for a country and year with no data"""
    result = await ghg_tool.run_impl(action="country_emissions", country="Atlantis", year=2050)
    assert 'error' in result
    assert "No data available for Atlantis in 2050" in result['error']

@pytest.mark.asyncio
async def test_run_impl_region_aggregation():
    """Test run_impl for region aggregation with gas type"""
    result = await ghg_tool.run_impl(action="region_aggregation", region="South America (Other)", gas_type="CH4")
    assert result['region'] == "South America (Other)"
    assert result['gas_type'] == "CH4"
    assert result['yearly_emissions'] == {2005: 237.81}  # Based on mock data

@pytest.mark.asyncio
async def test_run_impl_emissions_trend_country():
    """Test run_impl for emissions trend of a country"""
    result = await ghg_tool.run_impl(action="emissions_trend", country="Germany")
    assert result['country'] == "Germany"
    assert result['trend'] == [{'Year': 2015, 'Value': 280.76}, {'Year': 2020, 'Value': 1594.00}]  # Based on mock data

@pytest.mark.asyncio
async def test_run_impl_compare_countries():
    """Test run_impl for comparing two countries"""
    result = await ghg_tool.run_impl(action="compare_countries", country="Germany", country2="United States")
    assert result['country_1'] == "Germany"
    assert result['country_2'] == "United States"
    
    # Expected comparison for available data in mock
    expected_comparison = [
        {'Year': 2020, 'Value_Germany': 1594.00, 'Value_United States': 1938.79}
    ]
    assert result['comparison'] == expected_comparison


@pytest.mark.asyncio
async def test_run_impl_total_global_emissions():
    """Test run_impl for total global emissions"""
    result = await ghg_tool.run_impl(action="total_global_emissions")
    assert "total_global_emissions" in result
    assert result['total_global_emissions'] == [{'Year': 2002, 'Value': 202.52}, {'Year': 2005, 'Value': 237.81}, {'Year': 2010, 'Value': 278.46}, {'Year': 2015, 'Value': 280.76}, {'Year': 2020, 'Value': 8646.71}]

@pytest.mark.asyncio
async def test_run_impl_total_emissions_by_gas():
    """Test run_impl for total emissions by gas type"""
    result = await ghg_tool.run_impl(action="total_emissions_by_gas", gas_type="CO2")
    assert result['gas_type'] == "CO2"
    assert result['yearly_emissions'] == [{'Year': 2002, 'Value': 202.52}, {'Year': 2015, 'Value': 280.76}, {'Year': 2020, 'Value': 3532.79}]

@pytest.mark.asyncio
async def test_run_impl_emissions_by_region():
    """Test run_impl for emissions by region"""
    result = await ghg_tool.run_impl(action="emissions_by_region")
    assert "emissions_by_region" in result
    
    # Sort the result to ensure consistency
    sorted_emissions_by_region = sorted(result['emissions_by_region'], key=lambda x: (x['World_Region'], x['Year']))
    expected_emissions_by_region = sorted([
        {'World_Region': 'Western Africa', 'Year': 2002, 'Value': 202.52},
        {'World_Region': 'South America (Other)', 'Year': 2005, 'Value': 237.81},
        {'World_Region': 'North America', 'Year': 2010, 'Value': 278.46},
        {'World_Region': 'Europe', 'Year': 2015, 'Value': 280.76},
        {'World_Region': 'Western Africa', 'Year': 2020, 'Value': 2412.99},
        {'World_Region': 'South America (Other)', 'Year': 2020, 'Value': 2700.93},
        {'World_Region': 'North America', 'Year': 2020, 'Value': 1938.79},
        {'World_Region': 'Europe', 'Year': 2020, 'Value': 1594.00}
    ], key=lambda x: (x['World_Region'], x['Year']))
    
    assert sorted_emissions_by_region == expected_emissions_by_region


@pytest.mark.asyncio
async def test_run_impl_top_n_countries_by_emissions():
    """Test run_impl for top N countries by emissions"""
    result = await ghg_tool.run_impl(action="top_n_countries_by_emissions", year=2020, top_n=2)
    assert result['year'] == 2020
    assert result['top_n_countries'] == [
        {"Country": "Suriname", "Value": 2700.93},
        {"Country": "Sao Tome and Principe", "Value": 2412.99}
    ]

@pytest.mark.asyncio
async def test_run_impl_percentage_change_emissions():
    """Test run_impl for percentage change in emissions"""
    result = await ghg_tool.run_impl(action="percentage_change_emissions", country="United States", start_year=2010, end_year=2020)
    assert result['start_year'] == 2010
    assert result['end_year'] == 2020
    assert result['percentage_change'] == pytest.approx(((1938.79 - 278.46) / 278.46) * 100)

@pytest.mark.asyncio
async def test_run_impl_highest_emissions_year():
    """Test run_impl for highest emissions year"""
    result = await ghg_tool.run_impl(action="highest_emissions_year", country="Suriname")
    assert result['highest_emissions_year'] == 2020
    assert result['highest_emissions_value'] == 2700.93

@pytest.mark.asyncio
async def test_run_impl_lowest_emissions_year():
    """Test run_impl for lowest emissions year"""
    result = await ghg_tool.run_impl(action="lowest_emissions_year", country="Suriname")
    assert result['lowest_emissions_year'] == 2005
    assert result['lowest_emissions_value'] == 237.81

@pytest.mark.asyncio
async def test_run_impl_cumulative_emissions():
    """Test run_impl for cumulative emissions over a period"""
    result = await ghg_tool.run_impl(action="cumulative_emissions", country="Suriname", start_year=2005, end_year=2020)
    assert result['start_year'] == 2005
    assert result['end_year'] == 2020
    # Cumulative emissions for Suriname in the mock data are 237.81 + 2700.93
    assert result['cumulative_emissions'] == pytest.approx(237.81 + 2700.93)

