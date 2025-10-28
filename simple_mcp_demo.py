#!/usr/bin/env python3
"""
Simple MCP Tools Demo
Direct demonstration of MCP server tools without LangChain dependencies

This is a fallback demo that directly imports and uses the MCP tools
without any LangChain/LangGraph dependencies for maximum compatibility.
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path to import server
sys.path.append(os.path.dirname(__file__))

# Load environment variables
load_dotenv()

# Import our MCP server tools directly
try:
    from server import web_search, roll_dice, get_weather
    print("✅ Successfully imported MCP tools")
except ImportError as e:
    print(f"❌ Error importing MCP tools: {e}")
    sys.exit(1)

def test_weather_tool():
    """Test the weather tool"""
    print("\n🌤️  Testing Weather Tool")
    print("-" * 40)
    
    cities = ["Tokyo", "New York", "London"]
    
    for city in cities:
        try:
            print(f"\n📍 Getting weather for {city}...")
            result = get_weather(city, "metric")
            print(result)
        except Exception as e:
            print(f"❌ Error getting weather for {city}: {e}")

def test_dice_tool():
    """Test the dice rolling tool"""
    print("\n🎲 Testing Dice Tool")
    print("-" * 40)
    
    dice_tests = [
        ("3d6", 1),  # 3 six-sided dice
        ("2d20k1", 2),  # 2 twenty-sided dice, keep highest, roll twice
        ("4d8", 1),  # 4 eight-sided dice
        ("1d100", 3)  # 1 hundred-sided die, roll 3 times
    ]
    
    for notation, num_rolls in dice_tests:
        try:
            print(f"\n🎯 Rolling {notation} ({num_rolls} time{'s' if num_rolls > 1 else ''}):")
            result = roll_dice(notation, num_rolls)
            print(result)
        except Exception as e:
            print(f"❌ Error rolling {notation}: {e}")

def test_web_search_tool():
    """Test the web search tool"""
    print("\n🔍 Testing Web Search Tool")
    print("-" * 40)
    
    queries = [
        "Model Context Protocol MCP",
        "LangGraph tutorial",
        "OpenWeatherMap API Python"
    ]
    
    for query in queries:
        try:
            print(f"\n🔎 Searching for: {query}")
            result = web_search(query)
            # Truncate long results for display
            if len(result) > 300:
                result = result[:300] + "..."
            print(result)
        except Exception as e:
            print(f"❌ Error searching for '{query}': {e}")

def interactive_mode():
    """Interactive mode to test tools"""
    print("\n🎮 Interactive Mode")
    print("Available commands:")
    print("  weather <city> [units] - Get weather (units: metric/imperial/kelvin)")
    print("  dice <notation> [num_rolls] - Roll dice (e.g., 3d6, 2d20k1)")
    print("  search <query> - Search the web")
    print("  quit - Exit")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n👤 Command: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            parts = user_input.split()
            command = parts[0].lower()
            
            if command == "weather":
                if len(parts) < 2:
                    print("❌ Usage: weather <city> [units]")
                    continue
                city = parts[1]
                units = parts[2] if len(parts) > 2 else "metric"
                try:
                    result = get_weather(city, units)
                    print(f"🌤️ {result}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            elif command == "dice":
                if len(parts) < 2:
                    print("❌ Usage: dice <notation> [num_rolls]")
                    continue
                notation = parts[1]
                num_rolls = int(parts[2]) if len(parts) > 2 else 1
                try:
                    result = roll_dice(notation, num_rolls)
                    print(f"🎲 {result}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            elif command == "search":
                if len(parts) < 2:
                    print("❌ Usage: search <query>")
                    continue
                query = " ".join(parts[1:])
                try:
                    result = web_search(query)
                    if len(result) > 500:
                        result = result[:500] + "..."
                    print(f"🔍 {result}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            else:
                print("❌ Unknown command. Try: weather, dice, search, or quit")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Environment Check")
    print("-" * 40)
    
    required_vars = {
        "TAVILY_API_KEY": "Web search functionality",
        "OPENWEATHER_API_KEY": "Weather functionality",
    }
    
    optional_vars = {
        "OPENAI_API_KEY": "LangGraph demo (optional for this simple demo)"
    }
    
    all_good = True
    
    for var, purpose in required_vars.items():
        if os.getenv(var):
            print(f"✅ {var} - {purpose}")
        else:
            print(f"❌ {var} - {purpose} (MISSING)")
            all_good = False
    
    for var, purpose in optional_vars.items():
        if os.getenv(var):
            print(f"✅ {var} - {purpose}")
        else:
            print(f"⚠️  {var} - {purpose} (optional)")
    
    if not all_good:
        print("\n❗ Some required API keys are missing. Please check environment_setup.md")
        return False
    
    print("\n✅ Environment looks good!")
    return True

def main():
    """Main demo function"""
    print("🚀 Simple MCP Tools Demo")
    print("Direct testing of MCP server tools")
    print("=" * 50)
    
    # Check environment
    env_ok = check_environment()
    
    print("\nChoose an option:")
    print("1. Run all demos")
    print("2. Interactive mode") 
    print("3. Test individual tools")
    print("4. Exit")
    
    choice = input("\nChoice [1]: ").strip() or "1"
    
    if choice == "1":
        if env_ok:
            test_dice_tool()      # This one doesn't need API keys
            test_weather_tool()   # Needs OPENWEATHER_API_KEY
            test_web_search_tool() # Needs TAVILY_API_KEY
        else:
            print("⚠️  Running dice tool only (no API keys required)...")
            test_dice_tool()
            
    elif choice == "2":
        interactive_mode()
        
    elif choice == "3":
        print("\nWhich tool to test?")
        print("1. Weather tool")
        print("2. Dice tool") 
        print("3. Web search tool")
        
        tool_choice = input("Choice [2]: ").strip() or "2"
        
        if tool_choice == "1":
            test_weather_tool()
        elif tool_choice == "2":
            test_dice_tool()
        elif tool_choice == "3":
            test_web_search_tool()
        else:
            print("Invalid choice")
            
    elif choice == "4":
        print("👋 Goodbye!")
        return
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
