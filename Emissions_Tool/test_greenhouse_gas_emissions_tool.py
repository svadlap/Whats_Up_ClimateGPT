# -*- coding: utf-8 -*-
"""
Created on: Wed Nov 2, 2024

Description: Pytest file for testing GreenhouseGasEmissionsTool

@author: Vishay Paka
"""

import pytest
import pandas as pd
from greenhouse_gas_emissions_tool import GreenhouseGasEmissionsTool

# Mock data for testing
mock_data = {
    'Country': ['India', 'Brazil', 'United States', 'Germany', 'India', 'Brazil', 'United States', 'Germany'],
    'Year': [2000, 2000, 2010, 2015, 2020, 2020, 2020, 2020],
    'World_Region': ['Asia', 'South America', 'North America', 'Europe', 'Asia', 'South America', 'North America', 'Europe'],
    'Substance': ['CO2', 'CH4', 'N2O', 'CO2', 'CH4', 'N2O', 'CO2', 'CO2'],
    'Value': [500, 600, 700, 800, 900, 1000, 1100, 1200]
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
    """Test run_impl for a valid country and year"""
    result = await ghg_tool.run_impl(action="country_emissions", country="India", year=2000)
    assert result['country'] == "India"
    assert result['year'] == 2000
    assert result['emissions'].iloc[0] == 500  

@pytest.mark.asyncio
async def test_run_impl_country_emissions_no_data():
    """Test run_impl for a country and year with no data"""
    result = await ghg_tool.run_impl(action="country_emissions", country="Atlantis", year=2050)
    assert 'error' in result
    assert "No data available" in result['error']

@pytest.mark.asyncio
async def test_run_impl_region_aggregation():
    """Test run_impl for region aggregation with gas type"""
    result = await ghg_tool.run_impl(action="region_aggregation", region="Asia", gas_type="CH4")
    assert result['region'] == "Asia"
    assert result['gas_type'] == "CH4"
    assert result['yearly_emissions'] == {2020: 900}

@pytest.mark.asyncio
async def test_run_impl_emissions_trend_country():
    """Test run_impl for emissions trend of a country"""
    result = await ghg_tool.run_impl(action="emissions_trend", country="India")
    assert result['country'] == "India"
    assert len(result['trend']) > 0

@pytest.mark.asyncio
async def test_run_impl_compare_countries():
    """Test run_impl for comparing two countries"""
    result = await ghg_tool.run_impl(action="compare_countries", country="India", region="Brazil")
    assert "comparison" in result
    assert len(result['comparison']) > 0

@pytest.mark.asyncio
async def test_run_impl_total_global_emissions():
    """Test run_impl for total global emissions"""
    result = await ghg_tool.run_impl(action="total_global_emissions")
    assert "total_global_emissions" in result
    assert len(result['total_global_emissions']) > 0

@pytest.mark.asyncio
async def test_run_impl_total_emissions_by_gas():
    """Test run_impl for total emissions by gas type"""
    result = await ghg_tool.run_impl(action="total_emissions_by_gas", gas_type="CO2")
    assert result['gas_type'] == "CO2"
    assert len(result['yearly_emissions']) > 0

@pytest.mark.asyncio
async def test_run_impl_emissions_by_region():
    """Test run_impl for emissions by region"""
    result = await ghg_tool.run_impl(action="emissions_by_region")
    assert "emissions_by_region" in result
    assert len(result['emissions_by_region']) > 0

@pytest.mark.asyncio
async def test_run_impl_top_n_countries_by_emissions():
    """Test run_impl for top N countries by emissions"""
    result = await ghg_tool.run_impl(action="top_n_countries_by_emissions", year=2020, top_n=2)
    assert result['year'] == 2020
    assert len(result['top_n_countries']) == 2

@pytest.mark.asyncio
async def test_run_impl_percentage_change_emissions():
    """Test run_impl for percentage change in emissions"""
    result = await ghg_tool.run_impl(action="percentage_change_emissions", country="India", start_year=2000, end_year=2020)
    assert "percentage_change" in result

@pytest.mark.asyncio
async def test_run_impl_highest_emissions_year():
    """Test run_impl for highest emissions year"""
    result = await ghg_tool.run_impl(action="highest_emissions_year", country="India")
    assert "highest_emissions_year" in result

@pytest.mark.asyncio
async def test_run_impl_lowest_emissions_year():
    """Test run_impl for lowest emissions year"""
    result = await ghg_tool.run_impl(action="lowest_emissions_year", country="Brazil")
    assert "lowest_emissions_year" in result

@pytest.mark.asyncio
async def test_run_impl_cumulative_emissions():
    """Test run_impl for cumulative emissions over a period"""
    result = await ghg_tool.run_impl(action="cumulative_emissions", country="India", start_year=2000, end_year=2020)
    assert "cumulative_emissions" in result
