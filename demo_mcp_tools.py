"""
Demo script to test MCP Server tools directly
This demonstrates the new API tools added for Activity #1
"""

import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def test_mcp_tools():
    """Test all the MCP server tools"""
    
    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "server.py"],
        env=None
    )
    
    print("🚀 Connecting to MCP Server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            print("✅ Connected to MCP Server!")
            print("📋 Available tools:")
            
            # List available tools
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n" + "="*50)
            print("🧪 Testing Tools")
            print("="*50)
            
            # Test web search
            print("\n1. Testing web_search...")
            try:
                result = await session.call_tool("web_search", {"query": "latest AI news"})
                print(f"✅ Web Search Result: {result.content[0].text[:200]}...")
            except Exception as e:
                print(f"❌ Web Search Error: {e}")
            
            # Test dice rolling
            print("\n2. Testing roll_dice...")
            try:
                result = await session.call_tool("roll_dice", {"notation": "2d20k1", "num_rolls": 3})
                print(f"✅ Dice Roll Result: {result.content[0].text}")
            except Exception as e:
                print(f"❌ Dice Roll Error: {e}")
            
            # Test weather (will show API key message if not configured)
            print("\n3. Testing get_weather...")
            try:
                result = await session.call_tool("get_weather", {"city": "San Francisco", "country_code": "US"})
                print(f"✅ Weather Result: {result.content[0].text}")
            except Exception as e:
                print(f"❌ Weather Error: {e}")
            
            # Test random joke
            print("\n4. Testing get_random_joke...")
            try:
                result = await session.call_tool("get_random_joke", {})
                print(f"✅ Joke Result: {result.content[0].text}")
            except Exception as e:
                print(f"❌ Joke Error: {e}")
            
            # Test QR code generation
            print("\n5. Testing generate_qr_code...")
            try:
                result = await session.call_tool("generate_qr_code", {"text": "Hello MCP World!", "size": "300x300"})
                print(f"✅ QR Code Result: {result.content[0].text}")
            except Exception as e:
                print(f"❌ QR Code Error: {e}")
            
            # Test cat fact
            print("\n6. Testing get_cat_fact...")
            try:
                result = await session.call_tool("get_cat_fact", {})
                print(f"✅ Cat Fact Result: {result.content[0].text}")
            except Exception as e:
                print(f"❌ Cat Fact Error: {e}")
            
            # Test random quote
            print("\n7. Testing get_random_quote...")
            try:
                result = await session.call_tool("get_random_quote", {})
                print(f"✅ Quote Result: {result.content[0].text}")
            except Exception as e:
                print(f"❌ Quote Error: {e}")
            
            print("\n" + "="*50)
            print("🎉 Demo completed!")
            print("="*50)


if __name__ == "__main__":
    print("MCP Server Tools Demo")
    print("Make sure your server.py is working and you have the required dependencies installed.")
    print("For weather functionality, add OPENWEATHER_API_KEY to your .env file.")
    print()
    
    try:
        asyncio.run(test_mcp_tools())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure to run 'uv sync' to install dependencies first.")


