"""
MCP Server Template
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field

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




@mcp.tool(
    title="Trello Summary",
    description="Trello Summary tool",
)
async def trello_summary() -> str:
    """Résumé de l’état des tickets Trello (ToDo, Doing, Done, Blocked)."""
    #return await trello_connector.sprint_summary()
    pass


if __name__ == "__main__":
    mcp.run(transport="streamable-http")