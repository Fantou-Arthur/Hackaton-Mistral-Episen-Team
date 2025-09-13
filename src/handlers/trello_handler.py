
import os
from dotenv import load_dotenv
from connectors import trello_connector 

class TrelloHandler:

    def __init__(self):
        load_dotenv()
        self.api = trello_connector.TrelloConnector(
            api_key=os.getenv("TRELLO_API_KEY"), 
            token=os.getenv("TRELLO_TOKEN")
        )

    def handleGetBoards(self):
        try:
            boards = self.api.get("members/me/boards")
            openBoards = [board for board in boards if not board.get('closed', False)]
            
            import json
            return {
                'content': [
                    {
                        'type': 'text',
                        'text': json.dumps([{'id': b['id'], 'name': b['name'], 'url': b['url'], 'desc': b['desc'], 'memberships': b['memberships']} for b in openBoards], indent=2)
                    }
                ]
            }
        except Exception as e:
            print(f"Error fetching boards: {e}")
            return None
    
    def handleGetList(self, board_id='68c54ba62ed16c399220c1bd'):
        try:
            lists = self.api.get(f"boards/{board_id}/lists")
            openLists = [lst for lst in lists if not lst.get('closed', False)]
            
            import json
            return {
                'content': [
                    {
                        'type': 'text',
                        'text': json.dumps([{'id': l['id'], 'name': l['name']} for l in openLists], indent=2)
                    }
                ]
            }
        except Exception as e:
            print(f"Error fetching lists: {e}")
            return None
        
    def handleGetCards(self, board_id='68c54ba62ed16c399220c1bd'):
        try:
            cards = self.api.get(f"boards/{board_id}/cards")
            import json
            return {
                'content': [
                    {
                        'type': 'text',
                        'text': json.dumps([{'id': c['id'], 'name': c['name'], 'due': c['due'], 'idList': c['idList'], 'idBoard': c['idBoard']} for c in cards], indent=2)
                    }
                ]
            }
        except Exception as e:
            print(f"Error fetching cards: {e}")
            return None
    
    def handleGetBoardDetails(self, board_id='68c54ba62ed16c399220c1bd'):
        try:
            board = self.api.get(f"boards/{board_id}")
            lists = self.api.get(f"boards/{board_id}/lists")
            cards = self.api.get(f"boards/{board_id}/cards")
            
            import json
            return {
                'content': [
                    {
                        'type': 'text',
                        'text': json.dumps({
                            'board': board,
                            'lists': lists,
                            'cards': cards
                        }, indent=2)
                    }
                ]
            }
        except Exception as e:
            print(f"Error fetching board details: {e}")
            return None