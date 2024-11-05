# -*- coding: utf-8 -*-
"""
Created on: Wed Nov 2, 2024

Description: Pytest file for testing CarbonEmissionsTool

@author: Vishay Paka
"""

import pytest
import pandas as pd
from carbon_emissions_tool import CarbonEmissionsTool

# Mock data for testing
mock_data = {
    'country': ['India', 'Brazil', 'United States', 'Germany', 'India', 'Brazil'],
    'date': ['01/01/2020', '02/02/2020', '03/03/2020', '04/04/2020', '05/05/2020', '06/06/2020'],
    'sector': ['Transport', 'Energy', 'Industry', 'Residential', 'Transport', 'Industry'],
    'MtCO2 per day': [10.5, 20.3, 15.0, 5.5, 12.1, 18.4]
}

# Create a DataFrame from the mock data
mock_df = pd.DataFrame(mock_data)
mock_df['date'] = pd.to_datetime(mock_df['date'], format='%d/%m/%Y')  # Convert the 'date' column to datetime

# Patch the global DataFrame in the CarbonEmissionsTool module
@pytest.fixture(autouse=True)
def patch_df(monkeypatch):
    monkeypatch.setattr("carbon_emissions_tool.df", mock_df)

# Initialize the tool
carbon_tool = CarbonEmissionsTool()

# Test cases for the CarbonEmissionsTool
def test_get_name():
    """Test the get_name method"""
    assert carbon_tool.get_name() == "get_carbon_emissions"

def test_get_description():
    """Test the get_description method"""
    description = carbon_tool.get_description()
    assert "Retrieve carbon emissions data" in description

def test_get_params_definition():
    """Test the get_params_definition method"""
    params = carbon_tool.get_params_definition()
    assert "country" in params
    assert "date" in params
    assert "sector" in params

@pytest.mark.asyncio
async def test_run_impl_valid_country():
    """Test run_impl with a valid country"""
    result = await carbon_tool.run_impl(country="India")
    assert result['country'] == "India"
    assert result['total_emissions'] == "22.6000 MtCO2"

@pytest.mark.asyncio
async def test_run_impl_invalid_country():
    """Test run_impl with an invalid country"""
    result = await carbon_tool.run_impl(country="Atlantis")
    assert 'error' in result[0] 

@pytest.mark.asyncio
async def test_run_impl_valid_date():
    """Test run_impl with a valid date"""
    result = await carbon_tool.run_impl(date="01/01/2020")
    assert result['date'] == "01/01/2020"
    assert result['total_emissions'] == "10.5000 MtCO2"

@pytest.mark.asyncio
async def test_run_impl_invalid_date_format():
    """Test run_impl with an invalid date format"""
    result = await carbon_tool.run_impl(date="2020-01-01")
    assert 'error' in result[0] 

@pytest.mark.asyncio
async def test_run_impl_date_range():
    """Test run_impl with a valid date range"""
    result = await carbon_tool.run_impl(start_date="01/01/2020", end_date="05/05/2020")
    assert "From 01/01/2020 to 05/05/2020" in result['date']
    assert result['total_emissions'] == "63.4000 MtCO2"

@pytest.mark.asyncio
async def test_run_impl_valid_sector():
    """Test run_impl with a valid sector"""
    result = await carbon_tool.run_impl(sector="Transport")
    assert result['sector'] == "Transport"
    assert result['total_emissions'] == "22.6000 MtCO2"

@pytest.mark.asyncio
async def test_run_impl_invalid_sector():
    """Test run_impl with an invalid sector"""
    result = await carbon_tool.run_impl(sector="Agriculture")
    assert 'error' in result[0]

@pytest.mark.asyncio
async def test_run_impl_no_matching_data():
    """Test run_impl when no data matches the criteria"""
    result = await carbon_tool.run_impl(country="Germany", date="01/01/2020")
    assert 'error' in result
    assert "No emissions data available" in result['error']
