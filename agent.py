from smolagents import ToolCallingAgent, ToolCollection, LiteLLMModel
from mcp import StdioServerParameters

# Specify Ollama LLM via LiteLLM
model = LiteLLMModel(
        model_id="ollama_chat/qwen2.5:1.5b",
        num_ctx=2048) 

server_parameters = StdioServerParameters(
    command="uv", args=["run", "server.py"]
)

with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
    agent = ToolCallingAgent(tools=tool_collection.tools, model=model)
