# -*- coding: utf-8 -*-
"""
Test file for WeatherDataTool

Created on: Wed Nov 15, 2024

Description: Pytest file for testing WeatherDataTool

@author: Vishay Paka
"""

import pytest
from current_weather_data_tool import WeatherDataTool
from unittest.mock import patch

# Initialize the tool
weather_tool = WeatherDataTool()

# Mock response for OpenWeather API
mock_response = {
    "main": {
        "temp": 281.36,
        "feels_like": 281.36,
        "temp_min": 280.23,
        "temp_max": 282.45,
        "pressure": 1018,
        "humidity": 83,
        "sea_level": 1018,
        "grnd_level": 1007
    },
    "wind": {"speed": 0, "deg": 0},
    "weather": [{"id": 501, "main": "Rain", "description": "moderate rain", "icon": "10d"}],
    "sys": {"country": "US", "sunrise": 1731585090, "sunset": 1731621393},
    "timezone": -18000,
    "name": "Fairfax",
    "cod": 200
}

# Patch the API request to return the mock response
@pytest.fixture
def mock_api_response(monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                return mock_response
        return MockResponse()
    monkeypatch.setattr("requests.get", mock_get)

# Test cases for WeatherDataTool
def test_get_name():
    """Test the get_name method"""
    assert weather_tool.get_name() == "weather_data_tool"

def test_get_description():
    """Test the get_description method"""
    description = weather_tool.get_description()
    assert "Retrieve current weather data" in description

def test_get_params_definition():
    """Test the get_params_definition method"""
    params = weather_tool.get_params_definition()
    assert "action" in params
    assert "city" in params

@pytest.mark.asyncio
async def test_run_impl_current_weather_data(mock_api_response):
    """Test run_impl for current weather data"""
    result = await weather_tool.run_impl(action="current_weather_data", city="Fairfax")
    assert result["city"] == "Fairfax"
    assert result["country"] == "US"
    assert "current_temperature" in result
    assert "temperature_range" in result
    assert "feels_like_temperature" in result
    assert "humidity" in result
    assert "wind_speed" in result
    assert "weather_description" in result
    assert "sunrise_time" in result
    assert "sunset_time" in result

@pytest.mark.asyncio
async def test_run_impl_comfort_index(mock_api_response):
    """Test run_impl for comfort index calculation"""
    result = await weather_tool.run_impl(action="comfort_index", city="Fairfax")
    assert result["city"] == "Fairfax"
    assert "comfort_index" in result
    assert result["temperature_celsius"] == pytest.approx(8.21, 0.1)  # Converted from 281.36K
    assert result["humidity"] == 83
    assert result["wind_speed"] == 0

@pytest.mark.asyncio
async def test_run_impl_fog_risk(mock_api_response):
    """Test run_impl for fog risk assessment"""
    result = await weather_tool.run_impl(action="fog_risk", city="Fairfax")
    assert result["city"] == "Fairfax"
    assert "fog_risk" in result
    assert result["temperature_celsius"] == pytest.approx(8.21, 0.1)  # Converted from 281.36K
    assert result["humidity"] == 83
    assert "dew_point_celsius" in result

@pytest.mark.asyncio
async def test_run_impl_invalid_action(mock_api_response):
    """Test run_impl for invalid action"""
    result = await weather_tool.run_impl(action="invalid_action", city="Fairfax")
    assert "error" in result
    assert "Invalid action" in result["error"]

@pytest.mark.asyncio
async def test_run_impl_no_data():
    """Test run_impl for non-existent city to handle error"""
    with patch("requests.get") as mock_get:
        # Mock the API response for a non-existent city
        mock_get.return_value.json.return_value = {"cod": "404", "message": "city not found"}
        result = await weather_tool.run_impl(action="current_weather_data", city="NonExistentCity")
        assert "error" in result
        assert "No data available for city 'NonExistentCity'" in result["error"]

