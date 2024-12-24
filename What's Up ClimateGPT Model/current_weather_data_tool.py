# -*- coding: utf-8 -*-
"""
Weather Data Tool with Modular Action-Based Functions and Standardized Response

Created on Thu Nov 14, 2024

@author: Vishay Paka
"""

import requests
from typing import Dict, Any
from custom_tools import SingleMessageCustomTool
from datetime import datetime as dt
from datetime import datetime, timezone
from llama_stack_client.types.tool_param_definition_param import ToolParamDefinitionParam

class WeatherDataTool(SingleMessageCustomTool):
    """
    Tool to retrieve weather data for a specified city using the OpenWeather API.
    This tool supports querying current weather conditions, comfort index, and fog risk.
    """

    def get_name(self) -> str:
        """Return the unique name of the tool used for invocation."""
        return "weather_data_tool"

    def get_description(self) -> str:
        """Provide a detailed description of the tool."""
        return (
            "Retrieve current weather data for a specified city, including temperature, "
            "humidity, wind speed, weather description, and optional analyses like "
            "comfort index and fog risk assessment."
        )

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        """
        Define the parameters accepted by the tool and their descriptions.
        """
        return {
            "city": ToolParamDefinitionParam(
                param_type="str",
                description="The city for which to fetch weather data, e.g., 'Fairfax'.",
                required=True,
            ),
            "action": ToolParamDefinitionParam(
                param_type="str",
                description="Type of analysis: 'current_weather_data', 'comfort_index', or 'fog_risk'.",
                required=True,
            ),
        }

    async def run_impl(self, city: str, action: str) -> Dict[str, Any]:
        """
        Execute the tool's main logic to retrieve weather data for a specified city.

        Parameters:
        - city (str): The name of the city for which to fetch weather data.
        - action (str): Type of analysis to perform.

        Returns:
        - Dict[str, Any]: A dictionary containing various weather metrics or an error message.
        """
        # OpenWeather API URL and key
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        api_key = "41442b97138cb50d7095212a63d59bf9"  # Replace with your actual API key
        url = f"{base_url}?appid={api_key}&q={city}"

        # Fetch data from the API
        response = requests.get(url).json()

        # Handle error if city data is not found
        if response.get("cod") != 200:
            return {"error": f"No data available for city '{city}'"}

        # Call specific analysis functions based on the action parameter
        if action == "current_weather_data":
            return self.current_weather_data(response, city)
        elif action == "comfort_index":
            return self.calculate_comfort_index(response, city)
        elif action == "fog_risk":
            return self.calculate_fog_risk(response, city)
        else:
            return {"error": f"Invalid action: '{action}'"}

    # Current weather information retrieval
    def current_weather_data(self, response: dict, city: str) -> Dict[str, Any]:
        """Retrieve current weather data."""
        
        # Helper function to convert Kelvin to Celsius and Fahrenheit
        def kelvin_to_celsius_fahrenheit(kelvin):
            celsius = kelvin - 273.15
            fahrenheit = celsius * (9/5) + 32
            return round(celsius, 2), round(fahrenheit, 2)

        # Extract data from the API response
        try:
            temp_kelvin = response['main']['temp']
            temp_min_kelvin = response['main']['temp_min']
            temp_max_kelvin = response['main']['temp_max']
            feels_like_kelvin = response['main']['feels_like']
            humidity = response['main']['humidity']
            wind_speed = response['wind']['speed']
            weather_description = response['weather'][0]['description']
            country = response['sys']['country']
            # Convert sunrise and sunset times to local time using timezone-aware datetime
            sunrise_time = dt.fromtimestamp(response['sys']['sunrise'] + response['timezone'], tz=timezone.utc)
            sunset_time = dt.fromtimestamp(response['sys']['sunset'] + response['timezone'], tz=timezone.utc)
        except KeyError:
            return {"error": f"Data retrieval issue for city '{city}'"}

        # Convert temperature values
        temp_celsius, temp_fahrenheit = kelvin_to_celsius_fahrenheit(temp_kelvin)
        temp_min_celsius, temp_min_fahrenheit = kelvin_to_celsius_fahrenheit(temp_min_kelvin)
        temp_max_celsius, temp_max_fahrenheit = kelvin_to_celsius_fahrenheit(temp_max_kelvin)
        feels_like_celsius, feels_like_fahrenheit = kelvin_to_celsius_fahrenheit(feels_like_kelvin)

        return {
            "city": city,
            "country": country,
            "current_temperature": {"celsius": temp_celsius, "fahrenheit": temp_fahrenheit},
            "temperature_range": {
                "min": {"celsius": temp_min_celsius, "fahrenheit": temp_min_fahrenheit},
                "max": {"celsius": temp_max_celsius, "fahrenheit": temp_max_fahrenheit}
            },
            "feels_like_temperature": {"celsius": feels_like_celsius, "fahrenheit": feels_like_fahrenheit},
            "humidity": humidity,
            "wind_speed": wind_speed,
            "weather_description": weather_description,
            "sunrise_time": sunrise_time.strftime("%Y-%m-%d %H:%M:%S"),
            "sunset_time": sunset_time.strftime("%Y-%m-%d %H:%M:%S")
        }

    # Calculate the comfort index based on temperature, humidity, and wind speed
    def calculate_comfort_index(self, response: dict, city: str) -> Dict[str, Any]:
        """Calculate a comfort index based on temperature, humidity, and wind speed."""
        
        # Extract temperature, humidity, and wind speed
        try:
            temp_kelvin = response['main']['temp']
            humidity = response['main']['humidity']
            wind_speed = response['wind']['speed']
        except KeyError:
            return {"error": f"Data retrieval issue for city '{city}'"}
        
        # Convert temperature to Celsius
        temp_celsius = temp_kelvin - 273.15

        # Determine comfort level
        if temp_celsius < 20 and humidity < 60:
            comfort_level = "Very Comfortable"
        elif temp_celsius < 30 and humidity < 70:
            comfort_level = "Comfortable"
        elif temp_celsius < 35 or humidity > 70:
            comfort_level = "Uncomfortable"
        else:
            comfort_level = "High Risk of Heat Stress"

        return {
            "city": city,
            "comfort_index": comfort_level,
            "temperature_celsius": round(temp_celsius, 2),
            "humidity": humidity,
            "wind_speed": wind_speed
        }

    # Calculate fog risk based on temperature and humidity
    def calculate_fog_risk(self, response: dict, city: str) -> Dict[str, Any]:
        """Calculate fog risk based on temperature and humidity."""
        
        # Extract temperature and humidity
        try:
            temp_kelvin = response['main']['temp']
            humidity = response['main']['humidity']
        except KeyError:
            return {"error": f"Data retrieval issue for city '{city}'"}
        
        # Convert temperature to Celsius
        temp_celsius = temp_kelvin - 273.15

        # Calculate dew point for fog risk assessment
        dew_point = temp_celsius - ((100 - humidity) / 5.0)
        fog_risk = "High Fog Risk" if dew_point >= temp_celsius - 1 else "Low Fog Risk"

        return {
            "city": city,
            "fog_risk": fog_risk,
            "temperature_celsius": round(temp_celsius, 2),
            "humidity": humidity,
            "dew_point_celsius": round(dew_point, 2)
        }
