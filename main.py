"""
MCP Server Template
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from dotenv import load_dotenv
from connectors.teams_connector import TeamsConnector
from handlers.teams_handler import TeamsHandler

  

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


@mcp.tool()
async def teams_find_team(name: str = Field(description="Nom (partiel) de l'équipe")) -> dict:
    """Retourne l'ID et infos d'une team par son nom."""
    res = await TeamsConnector.find_team_by_name(name)
    return res or {"error": f"Aucune team trouvée pour {name}"}

@mcp.tool()
async def teams_find_channel(
    team_id: str = Field(description="ID de la team"),
    name: str = Field(description="Nom (partiel) du canal")
) -> dict:
    """Retourne l'ID et infos d'un canal par son nom."""
    res = await TeamsConnector.find_channel_by_name(team_id, name)
    return res or {"error": f"Aucun canal trouvé pour {name}"}

@mcp.tool()
async def teams_find_user(
    email: str = Field(description="Email ou UserPrincipalName de l'utilisateur")
) -> dict:
    """Retourne l'ID Graph d'un utilisateur par son email."""
    res = await TeamsConnector.find_user_by_email(email)
    return res or {"error": f"Aucun utilisateur trouvé pour {email}"}



@mcp.tool(
    title="Great User",
    description="Great the user",
)
def Greet(User: str = Field(description="The User to greet")) -> str:
    Greetings = "Hello dear user :"+User
    return Greetings


@mcp.tool(
    title="Teams Summary",
    description="Get a summary of recent messages and mentions in the main Teams channel.",
)
async def teams_summary() -> str:
    """Teams Summary: Number of recent messages and mentions in a given channel."""
    try:
        handler = TeamsHandler()
        response = handler.handleGetUnreadAndMentions()

        if response and 'content' in response and response['content']:
            return response['content'][0].get('text', "Error: The response format is incorrect.")
        else:
            return "Unable to retrieve the summary from Teams (empty response)."
    except Exception as e:
        print(f"An error occurred in teams_summary: {e}")
        return f"Sorry, an error occurred while contacting Teams."


@mcp.tool(
    title="Send_Message_Teams",
    description="Send the input message to a designated channel or a user",
)
async def teams_send_message(text: str = Field(description="Contenu (HTML ou texte)")) -> str:
    """Poster un message dans le canal Teams configuré."""
    return await TeamsConnector.send_channel_message(text)

@mcp.tool(
    title="Reply_Message_Teams",
    description="Answer in a thread on teams",
)
async def teams_reply(parent_message_id: str = Field(description="ID du message parent"),
                      text: str = Field(description="Contenu (HTML ou texte)")) -> str:
    """Répondre à un fil dans le canal."""
    return await TeamsConnector.reply_to_message(parent_message_id, text)


@mcp.tool(
    title="Mention_People_Teams",
    description="Send the input message to a designated channel or a user and ping the user",
)
async def teams_send_mention(user_id: str = Field(description="ID Graph de l'utilisateur mentionné"),
                             display_name: str = Field(description="Nom à afficher"),
                             text: str = Field(description="Texte additionnel")) -> str:
    """Envoyer un message avec @mention d'un utilisateur."""
    return await TeamsConnector.send_with_mention(user_id, display_name, text)


@mcp.tool(
    title="Trello Summary",
    description="Trello Summary tool",
)
async def trello_summary() -> str:
    """Résumé de l’état des tickets Trello (ToDo, Doing, Done, Blocked)."""
    #return await trello_connector.sprint_summary()
    pass


@mcp.tool(
    title="List All Users",
    description="Retourne tous les utilisateurs Azure AD via Microsoft Graph /users (avec pagination).",
)
async def teams_list_users(
    select: str = Field(
        default="id,displayName,mail,userPrincipalName",
        description="Champs à retourner (CSV) pour $select."
    ),
    filter_expr: str | None = Field(
        default=None,
        description="Filtre OData optionnel, ex: \"accountEnabled eq true\""
    ),
    page_size: int = Field(
        default=50,
        description="Taille de page ($top)."
    )
) -> dict:
    """
    Expose la liste des utilisateurs au travers de l'outil MCP.
    Renvoie un objet {count, users}.
    """
    try:
        users = await TeamsConnector.list_all_users(
            select=select, filter_expr=filter_expr, page_size=page_size
        )
        return {"count": len(users), "users": users}
    except Exception as e:
        return {"error": f"teams_list_users failed: {e!s}"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")