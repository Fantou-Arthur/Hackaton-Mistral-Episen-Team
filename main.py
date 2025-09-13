"""
MCP Server Template
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from dotenv import load_dotenv
from connectors import teams_connector

  

mcp = FastMCP("EPISEN_AI_TEAM_SUPPORT", port=3000, stateless_http=True, debug=True)



env_file = os.getenv("ENV_FILE", ".env.production")

print(f" Loading env file: {env_file}")
load_dotenv(env_file)


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
    title="teams_summary",
    description="Get the ping and the unread messages, you'll have to summarize that after receiving the info",
)
async def teams_summary() -> str:
    """Résumé Teams (messages récents + mentions)."""
    return await teams_connector.unread_and_mentions()

@mcp.tool(
    title="Send_Message_Teams",
    description="Send the input message to a designated channel or a user",
)
async def teams_send_message(text: str = Field(description="Contenu (HTML ou texte)")) -> str:
    """Poster un message dans le canal Teams configuré."""
    return await teams_connector.send_channel_message(text)

@mcp.tool(
    title="Reply_Message_Teams",
    description="Answer in a thread on teams",
)
async def teams_reply(parent_message_id: str = Field(description="ID du message parent"),
                      text: str = Field(description="Contenu (HTML ou texte)")) -> str:
    """Répondre à un fil dans le canal."""
    return await teams_connector.reply_to_message(parent_message_id, text)


@mcp.tool(
    title="Mention_People_Teams",
    description="Send the input message to a designated channel or a user and ping the user",
)
async def teams_send_mention(user_id: str = Field(description="ID Graph de l'utilisateur mentionné"),
                             display_name: str = Field(description="Nom à afficher"),
                             text: str = Field(description="Texte additionnel")) -> str:
    """Envoyer un message avec @mention d'un utilisateur."""
    return await teams_connector.send_with_mention(user_id, display_name, text)


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