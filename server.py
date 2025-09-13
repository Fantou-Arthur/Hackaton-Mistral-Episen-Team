from mcp.server.fastmcp import FastMCP
from connectors import trello_connector, slack_connector, ga4_connector

mcp = FastMCP("ai-team-dashboard")

@mcp.tool()
async def trello_summary() -> str:
    """Résumé de l’état des tickets Trello (ToDo, Doing, Done, Blocked)."""
    return await trello_connector.sprint_summary()

@mcp.tool()
async def slack_summary() -> str:
    """Résumé des unread messages et mentions Slack."""
    return await slack_connector.unread_mentions()

@mcp.tool()
async def ga4_summary() -> str:
    """Résumé des sessions utilisateurs sur les 7 derniers jours (GA4)."""
    return await ga4_connector.sessions_report()

if __name__ == "__main__":
    mcp.run(transport="stdio")  # stdio pour Claude / http si tu veux tester REST
