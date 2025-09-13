"""
MCP Server Template
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from tools.methods import ToolsMethods
from tools.mistral import MistralAI

MistralClient = MistralAI() 

mcp = FastMCP("EPISEN_AI_TEAM_SUPPORT", port=3000, stateless_http=True, debug=True)


@mcp.tool(
    title="Echo Tool",
    description="Echo the input text",
)
def echo(text: str = Field(description="The text to echo")) -> str:
    return text




@mcp.tool(
    title="Great User",
    description="Great the user",
)
def Greet(User: str = Field(description="The User to greet")) -> str:
    Greetings = "Hello dear user :"+User
    return Greetings

# @mcp.tool()
# async def teams_summary() -> str:
#     """Résumé Teams (messages récents + mentions)."""
#     return await teams_connector.unread_and_mentions()


@mcp.tool(
    title="Trello Summary",
    description="Trello Summary tool",
)
async def trello_summary(project_name: str = Field(description="The name of the project the user want to summarize")) -> str:
    """Résumé de l’état des tickets Trello (ToDo, Doing, Done, Blocked)."""
    boardId = MistralClient.getboardId("hackathon planning")
    if boardId is None:
        return "No project found with the given name."
    else:
        return ToolsMethods().boardDataForSummary(boardId)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")