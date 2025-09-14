from dotenv import load_dotenv
from handlers import trello_handler

class ToolsMethods:
    def __init__(self):
        load_dotenv()
        self.trello = trello_handler.TrelloHandler()

    def boardDataForSummary(self, board_id):
        try:
            board = self.trello.handleGetBoardDetails(board_id)
            lists = self.trello.handleGetListForBoard(board_id)
            cards = self.trello.handleGetCardsForBoard(board_id)

            import json
            return json.dumps({
                'board': board,
                'lists': lists,
                'cards': cards
            }, indent=2)
        except Exception as e:
            print(f"Error fetching board details: {e}")
            return None

    def getOverdueTaskWithMembers(self, board_id, dateLimit=None):
        try:
            cards = self.trello.handleGetTaskOverdue(board_id, dateLimit)            
            for card in cards:
                member_details = []
                for member_id in card.get('idMembers', []):
                    member_info = self.trello.handleGetMemberDetails(member_id)
                    if member_info:
                        member_details.append(member_info)
                card['memberDetails'] = member_details
            import json
            return json.dumps({
                'board_id': json.dumps(board_id, indent=2),
                'overdue_cards': json.dumps(cards, indent=2)
            }, indent=2)
        except Exception as e:
            print(f"Error fetching overdue tasks: {e}")
            return None
        
    def addCommentToCard(self, card_id, comment_text):
        try:
            response = self.trello.handleAddCommentToCard(card_id, comment_text)
            import json
            return json.dumps(response, indent=2)
        except Exception as e:
            print(f"Error adding comment to card: {e}")
            return None

    def GetDueDatesfromincompleteTask(self, board_id):
        try:
            dates = self.trello.handleboardGetdate(board_id)
            event_details = []
            for date in dates:
                if date["dueComplete"] == False:
                    event_details.append(date)
            import json
            return json.dumps(event_details, indent=2)

        except Exception as e:
            print(f"Error fetching board details: {e}")
            return None

    def getBoardMembers(self, board_id):
        try:
            members = self.trello.handleGetBoardMembers(board_id)
            import json
            return json.dumps(members, indent=2)
        except Exception as e:
            print(f"Error fetching board members: {e}")
            return None

    def assignMemberToTask(self, card_id, member_id):
        try:
            response = self.trello.handleAssignMemberToCard(card_id, member_id)
            import json
            return json.dumps(response, indent=2)
        except Exception as e:
            print(f"Error assigning member to card: {e}")
            return None

    def removeMemberFromTask(self, card_id, member_id):
        try:
            response = self.trello.handleRemoveMemberFromCard(card_id, member_id)
            import json
            return json.dumps(response, indent=2)
        except Exception as e:
            print(f"Error removing member from card: {e}")
            return None

    def addNewTaskToList(self, list_id, task_name, task_desc=""):
        try:
            response = self.trello.handleAddCardToList(list_id, task_name, task_desc)
            import json
            return json.dumps(response, indent=2)
        except Exception as e:
            print(f"Error adding new card to list: {e}")
            return None
    
    def getAllBoardLists(self, board_id):
        try:
            lists = self.trello.handleGetListForBoard(board_id)
            import json
            return json.dumps(lists, indent=2)
        except Exception as e:
            print(f"Error fetching board lists: {e}")
            return None