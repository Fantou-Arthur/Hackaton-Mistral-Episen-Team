"""
MCP Server Template
"""
import datetime
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from tools.methods import ToolsMethods
from tools.mistral import MistralAI
from handlers.teams_handler import TeamsHandler

MistralClient = MistralAI() 

mcp = FastMCP("EPISEN_AI_TEAM_SUPPORT", port=3000, stateless_http=True, debug=True)

load_dotenv()

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
    boardId = MistralClient.getboardId(project_name)
    if boardId is None:
        return "No project found with the given name."
    else:
        return ToolsMethods().boardDataForSummary(boardId)
    
@mcp.tool(
    title="Trello Project Overdue Tasks",
    description="Get overdue tasks for a specific Trello project",
)
async def trello_project_overdue_tasks(project_name: str = Field(description="The name of the project to get overdue tasks for"), dueDate: datetime = Field(description="The date to check for overdue tasks")) -> str:
    boardId = MistralClient.getboardId(project_name)
    if boardId is None:
        return "No project found with the given name."
    else:
        return ToolsMethods().getOverdueTaskWithMembers(boardId, dueDate)

@mcp.tool(
    title="Add Comment to Trello Task",
    description="Add a comment to a specific Trello Task",
)
async def add_comment_to_trello_task(card_id: str = Field(description="The ID of the Trello Task to comment on"), comment_text: str = Field(description="The comment text to add")) -> str:
    return ToolsMethods().addCommentToCard(card_id, comment_text)

@mcp.tool(
    title="Get Trello Board Members",
    description="Get members of a specific Trello Board",
)
async def get_trello_board_members(board_id: str = Field(description="The ID of the Trello Board to get members from")) -> str:
    return ToolsMethods().getBoardMembers(board_id)

@mcp.tool(
    title="Assign Task to Member",
    description="Assign a Trello Task to a specific member",
)
async def assign_task_to_member(card_id: str = Field(description="The ID of the Trello Task to assign"), member_id: str = Field(description="The ID of the member to assign the task to")) -> str:
    try:
        return ToolsMethods().assignMemberToTask(card_id, member_id)
    except Exception as e:
        print(f"Error assigning member to card: {e}")
        return None
    
@mcp.tool(
    title="Remove Task from Member",
    description="Remove a Trello Task from a specific member",
)
async def remove_task_from_member(card_id: str = Field(description="The ID of the Trello Task to remove"), member_id: str = Field(description="The ID of the member to remove the task from")) -> str:
    try:
        return ToolsMethods().removeMemberFromTask(card_id, member_id)
    except Exception as e:
        print(f"Error removing member from card: {e}")
        return None


@mcp.tool(
    title="Trello Due date from imcompleteTask",
    description="Tell the Due date from imcompleteTask",
)
async def trello_Due_date_from_imcompleteTask(project_name: str = Field(description="Get the due dates for all incomplete tasks from a Trello board")) -> str:
    try:
        boardId = MistralClient.getboardId(project_name)
        return ToolsMethods().GetDueDatesfromincompleteTask(boardId)
    except Exception as e:
        return "An error occurred while trying to fetch Trello data. The Trello API might be unavailable."

@mcp.tool(
    title="Add New Task to List",
    description="Add a new task to a specific Trello List",
)
async def add_new_task_to_list(list_id: str = Field(description="The ID of the Trello List to add the task to"), task_name: str = Field(description="The name of the task to add"), task_desc: str = Field(description="The description of the task to add")) -> str:
    return ToolsMethods().addNewTaskToList(list_id, task_name, task_desc)

@mcp.tool(
    title="Get all Lists",
    description="Get all Lists from Trello Board",
)
async def get_all_lists(board_id: str = Field(description="The ID of the Trello Board to get lists from")) -> str:
    try:
        return ToolsMethods().getAllBoardLists(board_id)
    except Exception as e:
        return "An error occurred while trying to fetch Trello data. The Trello API might be unavailable."


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
