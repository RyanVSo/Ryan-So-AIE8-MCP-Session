#!/usr/bin/env python3
"""
LangGraph Application that interacts with MCP Server
Activity #2 implementation for AIE8-MCP-Session

This application creates a simple agent that can use the MCP tools:
- web_search (Tavily API)
- roll_dice (Dice roller)
- get_weather (OpenWeatherMap API)
"""

import os
import json
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
import subprocess
import sys

# Load environment variables
load_dotenv()

# State for our graph
class AgentState(BaseModel):
    messages: List[Any] = Field(default_factory=list)

class MCPToolWrapper:
    """Wrapper to execute MCP tools via subprocess"""
    
    def __init__(self):
        self.server_path = os.path.join(os.path.dirname(__file__), "server.py")
    
    def _execute_mcp_tool(self, tool_name: str, **kwargs):
        """Execute an MCP tool by running the server in a subprocess"""
        try:
            # Create a simple script to call the MCP tool
            script = f"""
import sys
import os
sys.path.append('{os.path.dirname(__file__)}')
from server import mcp

# Get the tool function
tool_func = None
for tool in mcp.tools:
    if tool.name == '{tool_name}':
        tool_func = tool.fn
        break

if tool_func:
    result = tool_func(**{kwargs})
    print(result)
else:
    print(f"Error: Tool '{tool_name}' not found")
"""
            
            # Write script to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script)
                temp_script = f.name
            
            try:
                # Execute the script
                result = subprocess.run(
                    [sys.executable, temp_script],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    return f"Error executing tool: {result.stderr}"
                    
            finally:
                # Clean up temporary file
                os.unlink(temp_script)
                
        except Exception as e:
            return f"Error: {str(e)}"

# Create wrapper instance
mcp_wrapper = MCPToolWrapper()

# Define LangChain tools that wrap our MCP tools
@tool
def web_search_tool(query: str) -> str:
    """Search the web for information about the given query"""
    return mcp_wrapper._execute_mcp_tool("web_search", query=query)

@tool
def dice_roll_tool(notation: str, num_rolls: int = 1) -> str:
    """Roll dice with the given notation (e.g., '2d20k1' for 2 20-sided dice, keep highest 1)"""
    return mcp_wrapper._execute_mcp_tool("roll_dice", notation=notation, num_rolls=num_rolls)

@tool
def weather_tool(city: str, units: str = "metric") -> str:
    """Get current weather information for a given city. Units can be 'metric', 'imperial', or 'kelvin'."""
    return mcp_wrapper._execute_mcp_tool("get_weather", city=city, units=units)

# Create the tools list
tools = [web_search_tool, dice_roll_tool, weather_tool]

# Initialize the language model
try:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    llm_with_tools = llm.bind_tools(tools)
except Exception as e:
    print(f"Error initializing OpenAI: {e}")
    print("Make sure to set OPENAI_API_KEY in your .env file")
    sys.exit(1)

def agent_node(state: AgentState) -> Dict[str, Any]:
    """Main agent node that processes messages and decides on tool usage"""
    response = llm_with_tools.invoke(state.messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end"""
    last_message = state.messages[-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

# Add edges
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)
workflow.add_edge("tools", "agent")

# Compile the graph
app = workflow.compile()

def run_agent(user_input: str) -> str:
    """Run the agent with a user input"""
    try:
        state = AgentState(messages=[HumanMessage(content=user_input)])
        
        print(f"🤖 Processing: {user_input}")
        print("=" * 50)
        
        # Run the agent
        result = app.invoke(state)
        
        # Get the final response
        final_message = result["messages"][-1]
        
        if hasattr(final_message, 'content'):
            return final_message.content
        else:
            return str(final_message)
            
    except Exception as e:
        return f"Error running agent: {str(e)}"

def main():
    """Main interactive loop"""
    print("🚀 LangGraph MCP Agent Started!")
    print("Available tools: web_search, dice_roll, weather")
    print("Type 'quit' to exit\n")
    
    # Example queries
    examples = [
        "Roll 3d6 dice twice",
        "What's the weather in Tokyo?",
        "Search for information about LangGraph",
        "Get weather in New York in Fahrenheit",
        "Roll 2d20k1 (2 twenty-sided dice, keep highest)"
    ]
    
    print("💡 Example queries:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    print()
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
            
            # Run the agent
            response = run_agent(user_input)
            print(f"🤖 Assistant: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
