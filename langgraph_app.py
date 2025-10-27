"""
LangGraph Application for Activity #2
This application interacts with our MCP Server using langchain-mcp-adapters
"""

import os
import asyncio
from typing import TypedDict, Annotated
from langgraph.graph import Graph, StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import Tool
from dotenv import load_dotenv

# Import MCP adapter - you may need to install: pip install langchain-mcp-adapters
try:
    from langchain_mcp import MCPToolkit
except ImportError:
    print("langchain-mcp not found. Please install with: pip install langchain-mcp")
    print("For now, we'll create a demo version without MCP integration.")
    MCPToolkit = None

load_dotenv()


class GraphState(TypedDict):
    """State of our LangGraph application"""
    messages: Annotated[list, add_messages]
    user_intent: str
    tool_results: list
    final_response: str


class MCPLangGraphApp:
    """LangGraph application that interacts with MCP Server"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.mcp_tools = self._initialize_mcp_tools()
        self.graph = self._build_graph()
    
    def _initialize_mcp_tools(self):
        """Initialize MCP tools if available"""
        if MCPToolkit is None:
            # Fallback tools for demo purposes
            return self._create_demo_tools()
        
        try:
            # Initialize MCP toolkit with our server
            toolkit = MCPToolkit(
                server_script_path="server.py",
                server_transport="stdio"
            )
            return toolkit.get_tools()
        except Exception as e:
            print(f"Failed to initialize MCP tools: {e}")
            return self._create_demo_tools()
    
    def _create_demo_tools(self):
        """Create demo tools that simulate MCP functionality"""
        def demo_web_search(query: str) -> str:
            return f"Demo: Would search the web for '{query}'"
        
        def demo_roll_dice(notation: str, num_rolls: int = 1) -> str:
            return f"Demo: Would roll {notation} {num_rolls} time(s)"
        
        def demo_get_weather(city: str, country_code: str = "") -> str:
            return f"Demo: Would get weather for {city} {country_code}"
        
        def demo_get_joke() -> str:
            return "Demo joke: Why do programmers prefer dark mode? Because light attracts bugs!"
        
        def demo_generate_qr(text: str, size: str = "200x200") -> str:
            return f"Demo: Would generate QR code for '{text}' with size {size}"
        
        return [
            Tool(name="web_search", description="Search the web", func=demo_web_search),
            Tool(name="roll_dice", description="Roll dice", func=demo_roll_dice),
            Tool(name="get_weather", description="Get weather", func=demo_get_weather),
            Tool(name="get_random_joke", description="Get a joke", func=demo_get_joke),
            Tool(name="generate_qr_code", description="Generate QR code", func=demo_generate_qr),
        ]
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("analyze_intent", self.analyze_intent)
        workflow.add_node("select_tools", self.select_tools)
        workflow.add_node("execute_tools", self.execute_tools)
        workflow.add_node("generate_response", self.generate_response)
        
        # Add edges
        workflow.set_entry_point("analyze_intent")
        workflow.add_edge("analyze_intent", "select_tools")
        workflow.add_edge("select_tools", "execute_tools")
        workflow.add_edge("execute_tools", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    async def analyze_intent(self, state: GraphState) -> GraphState:
        """Analyze user intent from the messages"""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        system_message = """
        Analyze the user's intent and categorize it into one of these types:
        - weather: User wants weather information
        - joke: User wants entertainment/jokes
        - search: User wants to search the web
        - dice: User wants to roll dice
        - qr: User wants to generate QR codes
        - quote: User wants inspirational quotes
        - cat_fact: User wants cat facts
        - general: General conversation
        
        Just return the category name.
        """
        
        response = await self.llm.ainvoke([
            SystemMessage(content=system_message),
            HumanMessage(content=last_message)
        ])
        
        intent = response.content.lower().strip()
        state["user_intent"] = intent
        
        return state
    
    async def select_tools(self, state: GraphState) -> GraphState:
        """Select appropriate tools based on user intent"""
        intent = state["user_intent"]
        tool_mapping = {
            "weather": ["get_weather"],
            "joke": ["get_random_joke"],
            "search": ["web_search"],
            "dice": ["roll_dice"],
            "qr": ["generate_qr_code"],
            "quote": ["get_random_quote"],
            "cat_fact": ["get_cat_fact"],
            "general": []
        }
        
        selected_tools = tool_mapping.get(intent, [])
        state["selected_tools"] = selected_tools
        
        return state
    
    async def execute_tools(self, state: GraphState) -> GraphState:
        """Execute the selected tools"""
        selected_tools = state.get("selected_tools", [])
        tool_results = []
        
        for tool_name in selected_tools:
            tool = next((t for t in self.mcp_tools if t.name == tool_name), None)
            if tool:
                try:
                    # For demo purposes, we'll simulate tool execution
                    # In real implementation, you'd parse user input for parameters
                    if tool_name == "get_weather":
                        result = tool.func("San Francisco", "US")
                    elif tool_name == "roll_dice":
                        result = tool.func("2d20", 1)
                    elif tool_name == "web_search":
                        messages = state["messages"]
                        query = messages[-1].content if messages else "AI news"
                        result = tool.func(query)
                    elif tool_name == "generate_qr_code":
                        messages = state["messages"]
                        text = messages[-1].content if messages else "Hello World"
                        result = tool.func(text)
                    else:
                        result = tool.func()
                    
                    tool_results.append({
                        "tool": tool_name,
                        "result": result
                    })
                except Exception as e:
                    tool_results.append({
                        "tool": tool_name,
                        "error": str(e)
                    })
        
        state["tool_results"] = tool_results
        return state
    
    async def generate_response(self, state: GraphState) -> GraphState:
        """Generate final response based on tool results"""
        messages = state["messages"]
        intent = state["user_intent"]
        tool_results = state.get("tool_results", [])
        
        if not tool_results:
            # Handle general conversation
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a helpful assistant. Respond naturally to the user."),
                *messages
            ])
            final_response = response.content
        else:
            # Generate response based on tool results
            tool_info = "\n".join([
                f"Tool {r['tool']}: {r.get('result', r.get('error', 'No result'))}"
                for r in tool_results
            ])
            
            system_message = f"""
            Based on the tool results below, provide a helpful response to the user.
            Keep it conversational and informative.
            
            Tool Results:
            {tool_info}
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_message),
                *messages
            ])
            final_response = response.content
        
        state["final_response"] = final_response
        state["messages"] = add_messages(state["messages"], [AIMessage(content=final_response)])
        
        return state
    
    async def run(self, user_input: str):
        """Run the LangGraph application with user input"""
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "user_intent": "",
            "tool_results": [],
            "final_response": ""
        }
        
        result = await self.graph.ainvoke(initial_state)
        return result["final_response"]


async def main():
    """Demo the LangGraph application"""
    app = MCPLangGraphApp()
    
    print("🚀 MCP LangGraph Application Started!")
    print("Available commands: weather, joke, search, dice, qr, quote, cat_fact, or general conversation")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            response = await app.run(user_input)
            print(f"Assistant: {response}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())


