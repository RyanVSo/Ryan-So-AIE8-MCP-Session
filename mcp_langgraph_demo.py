#!/usr/bin/env python3
"""
Simplified LangGraph + MCP Integration Demo
Activity #2 implementation using direct MCP integration

This demo shows how to create a simple agent that can use MCP tools
in a more direct way by importing and using the MCP server tools directly.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import Field as PydanticField
import sys

# Add current directory to path to import server
sys.path.append(os.path.dirname(__file__))

# Load environment variables
load_dotenv()

# Import our MCP server tools
try:
    from server import web_search, roll_dice, get_weather
    print("✅ Successfully imported MCP tools")
except ImportError as e:
    print(f"❌ Error importing MCP tools: {e}")
    sys.exit(1)

# State for our graph
class AgentState(BaseModel):
    messages: List[Any] = Field(default_factory=list)
    tool_responses: List[str] = Field(default_factory=list)

# Input schemas for tools
class WebSearchInput(BaseModel):
    query: str = PydanticField(description="The search query to look up")

class DiceRollInput(BaseModel):
    notation: str = PydanticField(description="Dice notation (e.g., '3d6', '2d20k1')")
    num_rolls: int = PydanticField(default=1, description="Number of times to roll")

class WeatherInput(BaseModel):
    city: str = PydanticField(description="City name to get weather for")
    units: str = PydanticField(default="metric", description="Units: metric, imperial, or kelvin")

# Create LangChain tools from MCP functions
def create_langchain_tools():
    """Create LangChain StructuredTool objects from our MCP functions"""
    
    web_search_tool = StructuredTool.from_function(
        func=web_search,
        name="web_search",
        description="Search the web for information about the given query",
        args_schema=WebSearchInput
    )
    
    dice_roll_tool = StructuredTool.from_function(
        func=roll_dice,
        name="roll_dice", 
        description="Roll dice with the given notation (e.g., '3d6' for 3 six-sided dice)",
        args_schema=DiceRollInput
    )
    
    weather_tool = StructuredTool.from_function(
        func=get_weather,
        name="get_weather",
        description="Get current weather information for a given city",
        args_schema=WeatherInput
    )
    
    return [web_search_tool, dice_roll_tool, weather_tool]

# Initialize tools and LLM
tools = create_langchain_tools()

try:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    llm_with_tools = llm.bind_tools(tools)
    print("✅ Successfully initialized OpenAI LLM")
except Exception as e:
    print(f"❌ Error initializing OpenAI: {e}")
    print("Make sure to set OPENAI_API_KEY in your .env file")
    sys.exit(1)

def agent_node(state: AgentState) -> Dict[str, Any]:
    """Main agent node that processes messages and decides on tool usage"""
    try:
        response = llm_with_tools.invoke(state.messages)
        return {"messages": state.messages + [response]}
    except Exception as e:
        error_msg = AIMessage(content=f"Error in agent: {str(e)}")
        return {"messages": state.messages + [error_msg]}

def tool_node(state: AgentState) -> Dict[str, Any]:
    """Execute tools based on the last AI message"""
    last_message = state.messages[-1]
    
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {"messages": state.messages}
    
    tool_messages = []
    
    for tool_call in last_message.tool_calls:
        try:
            # Find the matching tool
            tool_func = None
            for tool in tools:
                if tool.name == tool_call["name"]:
                    tool_func = tool.func
                    break
            
            if tool_func:
                # Execute the tool
                result = tool_func(**tool_call["args"])
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
                tool_messages.append(tool_message)
            else:
                error_message = ToolMessage(
                    content=f"Error: Tool '{tool_call['name']}' not found",
                    tool_call_id=tool_call["id"]
                )
                tool_messages.append(error_message)
                
        except Exception as e:
            error_message = ToolMessage(
                content=f"Error executing tool: {str(e)}",
                tool_call_id=tool_call["id"]
            )
            tool_messages.append(error_message)
    
    return {"messages": state.messages + tool_messages}

def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end"""
    if not state.messages:
        return END
        
    last_message = state.messages[-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

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

def run_query(user_input: str) -> str:
    """Run a single query through the agent"""
    try:
        initial_state = AgentState(messages=[HumanMessage(content=user_input)])
        
        print(f"🔄 Processing: {user_input}")
        
        # Run the workflow
        final_state = app.invoke(initial_state)
        
        # Get the final response
        if final_state["messages"]:
            last_message = final_state["messages"][-1]
            if hasattr(last_message, 'content'):
                return last_message.content
            else:
                return str(last_message)
        
        return "No response generated"
        
    except Exception as e:
        return f"Error: {str(e)}"

def demo_queries():
    """Run some demo queries to showcase the functionality"""
    
    print("🚀 MCP + LangGraph Integration Demo")
    print("=" * 50)
    
    demo_queries = [
        "Roll 3 six-sided dice",
        "What's the weather like in San Francisco?", 
        "Search for information about Model Context Protocol",
        "Roll 2d20k1 and explain what that means",
        "Get weather in London using Celsius"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔍 Demo Query {i}: {query}")
        print("-" * 40)
        
        response = run_query(query)
        print(f"🤖 Response: {response}")
        
        # Add a small delay between queries
        import time
        time.sleep(1)

def interactive_mode():
    """Run in interactive mode"""
    print("\n🎮 Interactive Mode")
    print("Type your queries (or 'quit' to exit):")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
            
            response = run_query(user_input)
            print(f"🤖 Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🌟 Welcome to the MCP + LangGraph Demo!")
    print("Available tools: web_search, roll_dice, get_weather")
    print()
    
    mode = input("Choose mode - (d)emo or (i)nteractive [d]: ").strip().lower()
    
    if mode.startswith('i'):
        interactive_mode()
    else:
        demo_queries()

if __name__ == "__main__":
    main()
