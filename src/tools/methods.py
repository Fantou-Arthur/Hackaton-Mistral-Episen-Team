import json
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
            overdue_cards = {
                'board_id': board_id,
                'overdue_cards': cards
            }
            return json.dumps(overdue_cards, indent=2)

        except Exception as e:
            print(f"Error fetching overdue tasks: {e}")
            return None
        
    def addCommentToCard(self, card_id, comment_text):
        try:
            response = self.trello.handleAddCommentToCard(card_id, comment_text)
            return json.dumps(response, indent=2)
        except Exception as e:
            print(f"Error adding comment to card: {e}")
            return None