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
def get_weather(city: str, country_code: str = "") -> str:
    """Get current weather information for a city. Optionally specify country code (e.g., 'US', 'GB')"""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "Weather API key not configured. Please set OPENWEATHER_API_KEY in your .env file."
        
        location = f"{city},{country_code}" if country_code else city
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather = data['weather'][0]
            main = data['main']
            wind = data.get('wind', {})
            
            result = f"Weather in {data['name']}, {data['sys']['country']}:\n"
            result += f"Temperature: {main['temp']}°C (feels like {main['feels_like']}°C)\n"
            result += f"Condition: {weather['description'].title()}\n"
            result += f"Humidity: {main['humidity']}%\n"
            if 'speed' in wind:
                result += f"Wind Speed: {wind['speed']} m/s\n"
            
            return result
        else:
            return f"Could not get weather data for {city}. Please check the city name and try again."
    except Exception as e:
        return f"Error getting weather data: {str(e)}"

@mcp.tool()
def get_random_joke() -> str:
    """Get a random programming joke to brighten your day"""
    try:
        response = requests.get("https://official-joke-api.appspot.com/jokes/programming/random")
        if response.status_code == 200:
            joke_data = response.json()[0]
            return f"{joke_data['setup']}\n\n{joke_data['punchline']}"
        else:
            # Fallback to general random joke
            response = requests.get("https://official-joke-api.appspot.com/random_joke")
            if response.status_code == 200:
                joke_data = response.json()
                return f"{joke_data['setup']}\n\n{joke_data['punchline']}"
            else:
                return "Sorry, I couldn't fetch a joke right now. Maybe try again later!"
    except Exception as e:
        return f"Error getting joke: {str(e)}"

@mcp.tool()
def generate_qr_code(text: str, size: str = "200x200") -> str:
    """Generate a QR code for any text. Size can be specified as 'WIDTHxHEIGHT' (e.g., '300x300')"""
    try:
        # Using qr-server.com API for QR code generation
        encoded_text = requests.utils.quote(text)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}&data={encoded_text}"
        
        return f"QR Code generated for: '{text}'\nQR Code URL: {qr_url}\n\nYou can open this URL in your browser to view or download the QR code."
    except Exception as e:
        return f"Error generating QR code: {str(e)}"

@mcp.tool()
def get_cat_fact() -> str:
    """Get a random interesting fact about cats"""
    try:
        response = requests.get("https://catfact.ninja/fact")
        if response.status_code == 200:
            fact_data = response.json()
            return f"🐱 Cat Fact: {fact_data['fact']}"
        else:
            return "Sorry, I couldn't fetch a cat fact right now. Meow try again later!"
    except Exception as e:
        return f"Error getting cat fact: {str(e)}"

@mcp.tool()
def get_random_quote() -> str:
    """Get an inspirational quote to motivate your day"""
    try:
        response = requests.get("https://api.quotable.io/random")
        if response.status_code == 200:
            quote_data = response.json()
            return f'"{quote_data["content"]}"\n\n— {quote_data["author"]}'
        else:
            return "Sorry, I couldn't fetch a quote right now. Keep being awesome anyway!"
    except Exception as e:
        return f"Error getting quote: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")