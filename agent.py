"""
agent.py — Standalone AI Agent (Testing/Debug Script)
------------------------------------------------------
This file is a standalone script for testing the MCP tools and AI agent
outside of the Flask web application. It is NOT imported by app.py.

To test the agent directly, run:
    uv run agent.py

The main web app (app.py) creates its own agent instance internally.
"""

from smolagents import ToolCallingAgent, ToolCollection, LiteLLMModel
from mcp import StdioServerParameters

# Use the same model as app.py for consistency
model = LiteLLMModel(
    model_id="ollama_chat/llama3.2:latest",
    num_ctx=2048
)

server_parameters = StdioServerParameters(
    command="uv", args=["run", "server.py"]
)

if __name__ == "__main__":
    print("Starting standalone Museum AI Agent (test mode)...")
    print("Type your question and press Enter. Type 'exit' to quit.\n")

    with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
        agent = ToolCallingAgent(tools=tool_collection.tools, model=model)

        while True:
            try:
                query = input("You: ").strip()
                if query.lower() in ("exit", "quit", "q"):
                    print("Goodbye!")
                    break
                if not query:
                    continue
                response = agent.run(query)
                print(f"\nAgent: {response}\n")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
