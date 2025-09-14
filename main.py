"""
MCP Server Template
"""
import datetime
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from tools.methods import ToolsMethods
from tools.mistral import MistralAI

MistralClient = MistralAI() 

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

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
