from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
import requests
import json
from dice_roller import DiceRoller

load_dotenv()

mcp = FastMCP("mcp-server")
client = TavilyClient(os.getenv("TAVILY_API_KEY"))

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for information about the given query"""
    search_results = client.get_search_context(query=query)
    return search_results

@mcp.tool()
def roll_dice(notation: str, num_rolls: int = 1) -> str:
    """Roll the dice with the given notation"""
    roller = DiceRoller(notation, num_rolls)
    return str(roller)

@mcp.tool()
def get_weather(city: str, units: str = "metric") -> str:
    """Get current weather information for a given city. Units can be 'metric', 'imperial', or 'kelvin'."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OpenWeatherMap API key not found. Please set OPENWEATHER_API_KEY in your .env file."
    
    try:
        # OpenWeatherMap API endpoint
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": units
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant weather information
        weather_info = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "description": data["weather"][0]["description"].title(),
            "wind_speed": data["wind"]["speed"],
            "visibility": data.get("visibility", "N/A")
        }
        
        # Format units
        temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
        speed_unit = "m/s" if units == "metric" else "mph" if units == "imperial" else "m/s"
        
        # Create formatted response
        result = f"""🌤️ Weather for {weather_info['city']}, {weather_info['country']}:
        
📍 Location: {weather_info['city']}, {weather_info['country']}
🌡️ Temperature: {weather_info['temperature']}{temp_unit} (feels like {weather_info['feels_like']}{temp_unit})
☁️ Condition: {weather_info['description']}
💧 Humidity: {weather_info['humidity']}%
🔽 Pressure: {weather_info['pressure']} hPa
💨 Wind Speed: {weather_info['wind_speed']} {speed_unit}
👁️ Visibility: {weather_info['visibility']} meters"""
        
        return result
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {str(e)}"
    except KeyError as e:
        return f"Error parsing weather data: Missing field {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")