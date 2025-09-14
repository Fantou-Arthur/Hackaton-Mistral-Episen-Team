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
from dateutil import parser as dtparser
import asyncio  # Ajouté pour compatibilité async si nécessaire

mcp = FastMCP("EPISEN_AI_TEAM_SUPPORT", port=3000, stateless_http=True, debug=True)

env_file = os.getenv("ENV_FILE", ".env.production")
AUTH_MODE = os.getenv("AUTH_MODE", "delegueted").lower()

print(f" Loading env file: {env_file}")
load_dotenv(env_file)

@mcp.tool(
    title="Echo Tool",
    description="Echo the input text",
)
def echo(text: str = Field(description="The text to echo")) -> str:
    return text

@mcp.tool(
    title="Greet User",
    description="Greet the user",
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
        response = await handler.handleGetUnreadAndMentions()

        if response and 'content' in response and response['content']:
            return response['content'][0].get('text', "Error: The response format is incorrect.")
        else:
            return "Unable to retrieve the summary from Teams (empty response)."
    except Exception as e:
        print(f"An error occurred in teams_summary: {e}")
        return f"Sorry, an error occurred while contacting Teams: {e}"

@mcp.tool(
    title="Teams Read Thread",
    description="Reads the content of a specific message thread in the main Teams channel, given the parent message ID.",
)
async def teams_read_thread(parent_message_id: str) -> str:
    """Reads a specific thread."""
    try:
        handler = TeamsHandler()
        response = await handler.handleGetThreadMessages(parent_message_id)

        if response and 'content' in response and isinstance(response['content'], list) and len(
                response['content']) > 0:
            return response['content'][0].get('text', "Erreur : le format de la réponse est incorrect.")
        else:
            return "Impossible de lire le thread de Teams (réponse vide)."
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du thread : {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams : {e}"

@mcp.tool(
    title="Reply_Message_Teams",
    description="Answer in a thread on teams",
)
async def teams_reply(parent_message_id: str = Field(description="ID du message parent"),
                      text: str = Field(description="Contenu (HTML ou texte)")) -> str:
    """Répondre à un fil dans le canal."""
    try:
        connector = TeamsConnector()
        return await connector.reply_to_message(parent_message_id, text)
    except Exception as e:
        print(f"Une erreur s'est produite lors de la réponse au thread : {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams : {e}"

@mcp.tool(
    title="Send_Message_Teams",
    description="Send the input message to a designated channel or a user",
)
async def teams_send_message(text: str = Field(description="Contenu (HTML ou texte)")) -> str:
    """Poster un message dans le canal Teams configuré."""
    try:
        connector = TeamsConnector()
        return await connector.send_channel_message(text)
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'envoi du message : {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams : {e}"

@mcp.tool(
    title="Mention_People_Teams",
    description="Send the input message to a designated channel or a user and ping the user",
)
async def teams_send_mention(user_id: str = Field(description="ID Graph de l'utilisateur mentionné"),
                             display_name: str = Field(description="Nom à afficher"),
                             text: str = Field(description="Texte additionnel")) -> str:
    """Envoyer un message avec @mention d'un utilisateur."""
    try:
        connector = TeamsConnector()
        return await connector.send_with_mention(user_id, display_name, text)
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'envoi de la mention : {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams : {e}"

@mcp.tool(
    title="Trello Summary",
    description="Trello Summary tool",
)
async def trello_summary() -> str:
    """Résumé de l’état des tickets Trello (ToDo, Doing, Done, Blocked)."""
    #return await trello_connector.sprint_summary()
    pass

@mcp.tool(
    title="Teams List Team Members",
    description="Lists all members of the main Teams team.",
)
async def teams_list_members() -> str:
    """Lists all team members."""
    try:
        handler = TeamsHandler()
        response = await handler.handleListTeamMembers()

        if response and 'content' in response and isinstance(response['content'], list) and len(
                response['content']) > 0:
            return response['content'][0].get('text', "Erreur : le format de la réponse est incorrect.")
        else:
            return "Impossible de lister les membres de l'équipe (réponse vide ou incorrecte)."

    except Exception as e:
        print(f"Une erreur s'est produite dans teams_list_members: {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams: {e}"

@mcp.tool(
    title="Teams List All Private Chats",
    description="Lists all your private chat IDs and the display names of the other participants.",
)
async def teams_list_private_chats() -> str:
    """Lists all your private chat IDs."""
    try:
        handler = TeamsHandler()
        response = await handler.handleListPrivateChats()

        if response and 'content' in response and isinstance(response['content'], list) and len(
                response['content']) > 0:
            return response['content'][0].get('text', "Erreur : le format de la réponse est incorrect.")
        else:
            return "Impossible de lister les discussions privées (réponse vide ou incorrecte)."

    except Exception as e:
        print(f"Une erreur s'est produite lors de la liste des discussions privées : {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams : {e}."

@mcp.tool(
    title="Teams Get Private Chat Messages",
    description="Gets messages from a private chat given its chat ID.",
)
async def teams_get_private_messages(chat_id: str) -> str:
    """Gets messages from a private chat with a specific chat ID."""
    try:
        handler = TeamsHandler()
        response = await handler.handleGetPrivateMessages(chat_id)

        if response and 'content' in response and isinstance(response['content'], list) and len(
                response['content']) > 0:
            return response['content'][0].get('text', "Erreur : le format de la réponse est incorrect.")
        else:
            return "Impossible de récupérer les messages privés (réponse vide ou incorrecte)."

    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture des messages privés : {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams : {e}."

@mcp.tool()
async def teams_find_team(name: str = Field(description="Nom (partiel) de l'équipe")) -> dict:
    """Retourne l'ID et infos d'une team par son nom."""
    try:
        connector = TeamsConnector()
        res = await connector.find_team_by_name(name)
        return res or {"error": f"Aucune team trouvée pour {name}"}
    except Exception as e:
        return {"error": f"teams_find_team failed: {e}"}

@mcp.tool()
async def teams_find_channel(
    team_id: str = Field(description="ID de la team"),
    name: str = Field(description="Nom (partiel) du canal")
) -> dict:
    """Retourne l'ID et infos d'un canal par son nom."""
    try:
        connector = TeamsConnector()
        res = await connector.find_channel_by_name(team_id, name)
        return res or {"error": f"Aucun canal trouvé pour {name}"}
    except Exception as e:
        return {"error": f"teams_find_channel failed: {e}"}

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
        connector = TeamsConnector()
        users = await connector.list_all_users(
            select=select, filter_expr=filter_expr, page_size=page_size
        )
        return {"count": len(users), "users": users}
    except Exception as e:
        return {"error": f"teams_list_users failed: {e!s}"}

def _parse_dt(s: str) -> str:
    """Convertit une date naturelle/ISO en 'YYYY-MM-DDTHH:MM:SS' (sans TZ)."""
    # On laisse le fuseau géré par 'timezone' côté Graph
    return dtparser.parse(s).replace(tzinfo=None).isoformat(timespec="seconds")

@mcp.tool(
    title="Planifier une réunion Teams",
    description="Crée un événement calendrier avec lien Teams et invite des participants."
)
async def schedule_teams_meeting(
    organizer_upn: str = Field(description="UPN de l'organisateur (compte qui s'authentifie)"),
    subject: str = Field(description="Sujet de la réunion"),
    start: str = Field(description="Début (ex: '2025-09-14 14:00' ou ISO 8601)"),
    end: str = Field(description="Fin (ex: '2025-09-14 15:00' ou ISO 8601)"),
    timezone: str = Field(default="Europe/Paris", description="Fuseau horaire (ex: 'Europe/Paris')"),
    attendees_csv: str = Field(default="", description="Emails des invités, séparés par des virgules"),
    body_html: str = Field(default="", description="Description/agenda en HTML"),
    location: str = Field(default="", description="Texte libre du lieu (optionnel)")
) -> dict:
    """
    Retour: event.id, joinUrl, échos des champs.
    """
    try:
        conn = TeamsConnector()
        start_iso = _parse_dt(start)
        end_iso   = _parse_dt(end)
        attendees = [x.strip() for x in attendees_csv.split(",")] if attendees_csv else []

        res = await conn.create_teams_meeting(
            organizer_upn=organizer_upn,
            subject=subject,
            start_iso=start_iso,
            end_iso=end_iso,
            timezone=timezone,
            attendees=attendees,
            body_html=body_html,
            location_display_name=(location or None),
        )
        return {
            "status": "created",
            "eventId": res["event"]["id"],
            "subject": subject,
            "start": res["event"]["start"],
            "end": res["event"]["end"],
            "joinUrl": res["joinUrl"],
            "attendees": attendees,
            "timezone": timezone,
        }
    except Exception as e:
        return {"error": f"schedule_teams_meeting failed: {e}"}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")