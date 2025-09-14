"""
MCP Server Template
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from dotenv import load_dotenv
from connectors import teams_connector
from handlers.teams_handler import TeamsHandler


mcp = FastMCP("EPISEN_AI_TEAM_SUPPORT", port=3000, stateless_http=True, debug=True)



env_file = os.getenv("ENV_FILE", ".env.production")

print(f" Loading env file: {env_file}")
load_dotenv(env_file)


@mcp.tool(
    title="Teams Summary",
    description="Get a summary of recent messages and mentions in the main Teams channel.",
)
async def teams_summary() -> str:
    """Teams Summary: Number of recent messages and mentions in a given channel."""
    try:
        # Initialise le handler qui gère la logique de communication avec Teams
        handler = TeamsHandler()

        # Appelle la méthode pour obtenir les messages du canal
        # La méthode handleGetChannelMessages gère l'authentification et la requête
        response = handler.handleGetChannelMessages()

        # Vérifie si la réponse a le format attendu et extrait le contenu
        if response and 'content' in response and isinstance(response['content'], list) and len(
                response['content']) > 0:
            return response['content'][0].get('text', "Erreur : le format de la réponse est incorrect.")
        else:
            return "Impossible de récupérer le résumé de Teams (réponse vide)."

    except Exception as e:
        print(f"Une erreur s'est produite dans teams_summary: {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams: {e}."


@mcp.tool(
    title="Teams Read Thread",
    description="Reads the content of a specific message thread in the main Teams channel, given the parent message ID.",
)
async def teams_read_thread(parent_message_id: str) -> str:
    """Reads a specific thread."""
    try:
        handler = TeamsHandler()
        response = handler.handleGetThreadMessages(parent_message_id)

        if response and 'content' in response and isinstance(response['content'], list) and len(
                response['content']) > 0:
            return response['content'][0].get('text', "Erreur : le format de la réponse est incorrect.")
        else:
            return "Impossible de lire le thread de Teams (réponse vide)."
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du thread : {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams : {e}."

@mcp.tool(
    title="Teams List Team Members",
    description="Lists all members of the main Teams team.",
)
async def teams_list_members() -> str:
    """Lists all team members."""
    try:
        handler = TeamsHandler()
        # The handler returns a dictionary.
        response = handler.handleListTeamMembers()

        # Check if the response is a dictionary with the expected structure
        if response and 'content' in response and isinstance(response['content'], list) and len(
                response['content']) > 0:
            # Extract the 'text' content from the dictionary and return it as a string
            return response['content'][0].get('text', "Erreur : le format de la réponse est incorrect.")
        else:
            return "Impossible de lister les membres de l'équipe (réponse vide ou incorrecte)."

    except Exception as e:
        print(f"Une erreur s'est produite dans teams_list_members: {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams: {e}."


@mcp.tool(
    title="Teams List All Private Chats",
    description="Lists all your private chat IDs and the display names of the other participants.",
)
async def teams_list_private_chats() -> str:
    """Lists all your private chat IDs."""
    try:
        handler = TeamsHandler()
        # Appel de la méthode qui retourne un dictionnaire
        response = handler.handleListPrivateChats()

        # Vérification du format de la réponse et extraction de la chaîne de caractères
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
        # The handler returns a dictionary. We need to extract the string.
        response = handler.handleGetPrivateMessages(chat_id)

        # Check if the response is valid and extract the string content
        if response and 'content' in response and isinstance(response['content'], list) and len(
                response['content']) > 0:
            return response['content'][0].get('text', "Erreur : le format de la réponse est incorrect.")
        else:
            return "Impossible de récupérer les messages privés (réponse vide ou incorrecte)."

    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture des messages privés : {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams : {e}."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")