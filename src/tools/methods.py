
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
            # return {
            #     'content': [
            #         {
            #             'type': 'text',
            #             'text': json.dumps({
            #                 'board': board,
            #                 'lists': lists,
            #                 'cards': cards
            #             }, indent=2)
            #         }
            #     ]
            # }
            return json.dumps({
                'board': board,
                'lists': lists,
                'cards': cards
            }, indent=2)
        except Exception as e:
            print(f"Error fetching board details: {e}")
            return None