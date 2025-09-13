"""
MCP Server Template
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field

import mcp.types as types

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
    return await trello_connector.sprint_summary()




@mcp.tool(
    title="Slack Summary",
    description="Slack Summary tool",
)
async def slack_summary() -> str:
    """Résumé des unread messages et mentions Slack."""
    return await slack_connector.unread_mentions()

@mcp.tool(
    title="Google Analytics Website Summary",
    description="Google Analytics Website Summary tool",)
async def ga4_summary() -> str:
    """Résumé des sessions utilisateurs sur les 7 derniers jours (GA4)."""
    return await ga4_connector.sessions_report()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")