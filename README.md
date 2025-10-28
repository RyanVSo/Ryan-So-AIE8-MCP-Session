<p align = "center" draggable=”false” ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">AI Makerspace: MCP Session Repo for Session 13</h1>

This project is a demonstration of the MCP (Model Context Protocol) server, which utilizes the Tavily API for web search capabilities. The server is designed to run in a standard input/output (stdio) transport mode.

## Project Overview

The MCP server is set up to handle web search queries using the Tavily API. It is built with the following key components:

- **TavilyClient**: A client for interacting with the Tavily API to perform web searches.

## Prerequisites

- Python 3.13 or higher
- A valid Tavily API key

## ⚠️NOTE FOR WINDOWS:⚠️

You'll need to install this on the *Windows* side of your OS. 

This will require getting two CLI tool for Powershell, which you can do as follows:

- `winget install astral-sh.uv`
- `winget install --id Git.Git -e --source winget`

After you have those CLI tools, please open Cursor *into Windows*.

Then, you can clone the repository using the following command in your Cursor terminal:

```bash
git clone https://AI-Maker-Space/AIE8-MCP-Session.git
```

After that, you can follow from Step 2. below!

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Configure environment variables**:
Copy the `.env.sample` to `.env` and add your Tavily API key:
   ```
   TAVILY_API_KEY=your_api_key_here
   ```

3. 🏗️ **Add a new tool to your MCP Server** 🏗️

Create a new tool in the `server.py` file, that's it!

## Running the MCP Server

To start the MCP server, you will need to add the following to your MCP Profile in Cursor:

> NOTE: To get to your MCP config. you can use the Command Pallete (CMD/CTRL+SHIFT+P) and select "View: Open MCP Settings" and replace the contents with the JSON blob below.

```
{
    "mcpServers":  {
        "mcp-server": {
            "command" : "uv",
            "args" : ["--directory", "/PATH/TO/REPOSITORY", "run", "server.py"]
        }
    }
}
```

The server will start and listen for commands via standard input/output.

## Usage

The server provides a `web_search` tool that can be used to search the web for information about a given query. This is achieved by calling the `web_search` function with the desired query string.

## Activities: 

There are a few activities for this assignment!

### ✅ Activity #1: COMPLETED

**Weather API Integration**: Added a weather tool using the OpenWeatherMap API!

The MCP server now includes:
- `web_search` - Search the web using Tavily API
- `roll_dice` - Roll dice with various notations (e.g., 3d6, 2d20k1)  
- `get_weather` - Get current weather for any city with detailed information

### ✅ Activity #2: COMPLETED

**LangGraph Application**: Built a complete LangGraph application that integrates with the MCP Server!

Files created:
- `mcp_langgraph_demo.py` - Main demo application with interactive and demo modes
- `langgraph_app.py` - Alternative implementation 
- `environment_setup.md` - Complete setup guide

## 🚀 New Tools Available

### Weather Tool
```python
get_weather(city: str, units: str = "metric") -> str
```
- Get current weather for any city
- Support for metric, imperial, or kelvin units
- Returns temperature, humidity, pressure, wind speed, visibility

### Enhanced Server
The MCP server (`server.py`) now includes robust error handling and formatted responses.

## 🎮 Testing the Implementation

### Option 1: Test via Cursor (MCP Client)
1. Set up your API keys in `.env` file (see `environment_setup.md`)
2. Update your MCP configuration in Cursor
3. Ask Cursor: "What's the weather in Tokyo?" or "Roll 3d6 dice"

### Option 2: Test via LangGraph Demo
1. Set up API keys in `.env` file
2. Run: `uv run python mcp_langgraph_demo.py`
3. Choose demo mode to see examples or interactive mode to test yourself

You can find details [here](https://github.com/langchain-ai/langchain-mcp-adapters)!
