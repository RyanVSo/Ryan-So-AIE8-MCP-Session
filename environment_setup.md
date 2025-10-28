# Environment Setup Guide

## Required API Keys

To use all the features of this MCP server, you'll need to set up the following API keys in a `.env` file:

### 1. Tavily API Key (for web search)
- Sign up at: https://tavily.com/
- Add to `.env`: `TAVILY_API_KEY=your_tavily_api_key_here`

### 2. OpenWeatherMap API Key (for weather data)
- Sign up at: https://openweathermap.org/api  
- Get a free API key
- Add to `.env`: `OPENWEATHER_API_KEY=your_openweather_api_key_here`

### 3. OpenAI API Key (for LangGraph demo)
- Get API key from: https://platform.openai.com/api-keys
- Add to `.env`: `OPENAI_API_KEY=your_openai_api_key_here`

## Sample .env file content:

```
# Copy these lines to a new .env file and fill in your actual API keys
TAVILY_API_KEY=your_tavily_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here  
OPENAI_API_KEY=your_openai_api_key_here
```

## Quick Setup Commands

1. Create the .env file:
   ```bash
   touch .env
   ```

2. Edit the .env file with your preferred editor and add the API keys above

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Test the MCP server tools:
   ```bash
   uv run python mcp_langgraph_demo.py
   ```
