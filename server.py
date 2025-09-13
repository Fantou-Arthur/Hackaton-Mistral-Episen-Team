import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from connectors import trello_connector, slack_connector, ga4_connector

env_file = os.getenv("ENV_FILE", ".env.production")
print(f"🔧 Loading env file: {env_file}")
load_dotenv(env_file)

mcp = FastMCP("EPISEN_AI_TEAM_SUPPORT", port=3000, stateless_http=True, debug=True)

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

@mcp.tool(
    title="Echo Tool",
    description="Echo the input text",
)
def echo(text: str = Field(description="The text to echo")) -> str:
    return text


@mcp.resource(
    uri="greeting://{name}",
    description="Get a personalized greeting",
    name="Greeting Resource",
)
def get_greeting(
    name: str,
) -> str:
    return f"Hello, {name}!"


@mcp.prompt("")
def greet_user(
    name: str = Field(description="The name of the person to greet"),
    style: str = Field(description="The style of the greeting", default="friendly"),
) -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")