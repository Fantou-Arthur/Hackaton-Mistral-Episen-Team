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
    title="Teams Reply to Thread",
    description="Replies to a specific message thread with new text.",
)
async def teams_reply_to_thread(parent_message_id: str, text: str) -> str:
    """Replies to a specific message thread."""
    try:
        handler = TeamsHandler()
        response = handler.handleReplyToMessage(parent_message_id, text)

        if response and 'content' in response and isinstance(response['content'], list) and len(response['content']) > 0:
            return response['content'][0].get('text', "Erreur : le format de la réponse est incorrect.")
        else:
            return "Impossible de répondre au thread de Teams (réponse vide)."
    except Exception as e:
        print(f"Une erreur s'est produite lors de la réponse au thread : {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams : {e}."


@mcp.tool(
    title="Send_Message_Teams",
    description="Send the input message to a designated channel or a user",
)
async def teams_send_message(text: str = Field(description="Contenu (HTML ou texte)")) -> str:
    """Poster un message dans le canal Teams configuré."""
    return await teams_connector.send_channel_message(text)

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
    title="Teams Get Private Chat Messages",
    description="Gets messages from a private chat given its chat ID.",
)
async def teams_get_private_messages(chat_id: str) -> str:
    """Gets messages from a private chat with a specific chat ID."""
    try:
        handler = TeamsHandler()
        return handler.handleGetPrivateMessages(chat_id)
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture des messages privés : {e}")
        return f"Désolé, une erreur s'est produite en contactant Teams : {e}."



if __name__ == "__main__":
    mcp.run(transport="streamable-http")