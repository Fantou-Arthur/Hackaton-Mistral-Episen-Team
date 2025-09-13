
import os
import json
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
            
            return [{'id': b['id'], 'name': b['name'], 'url': b['url'], 'desc': b['desc'], 'memberships': b['memberships']} for b in openBoards]

        except Exception as e:
            print(f"Error fetching boards: {e}")
            return None
        
    def handleGetBoardDetails(self, board_id):
        try:
            board = self.api.get(f"boards/{board_id}")
            return [{'id': board['id'], 'name': board['name'], 'url': board['url'], 'desc': board['desc']}]
                    
        except Exception as e:
            print(f"Error fetching board details: {e}")
            return None
    
    def handleGetListForBoard(self, board_id):
        try:
            lists = self.api.get(f"boards/{board_id}/lists")
            openLists = [lst for lst in lists if not lst.get('closed', False)]
            
            return [{'id': l['id'], 'name': l['name'], 'idBoard': l['idBoard']} for l in openLists]
                    
        except Exception as e:
            print(f"Error fetching lists: {e}")
            return None
        
    def handleGetCardsForBoard(self, board_id):
        try:
            cards = self.api.get(f"boards/{board_id}/cards")
            
            return [{'id': c['id'], 'name': c['name'], 'due': c['due'], 'idList': c['idList'], 'idBoard': c['idBoard'], 'dueComplete': c['dueComplete'], 'desc': c['desc'], 'idMembers': c['idMembers']} for c in cards]
                    
        except Exception as e:
            print(f"Error fetching cards: {e}")
            return None

    def handleGetMemberDetails(self, member_id):
        try:
            member = self.api.get(f"members/{member_id}")
            return {'id': member['id'], 'fullName': member['fullName'], 'username': member['username']}
                    
        except Exception as e:
            print(f"Error fetching member details: {e}")
            return None
        
    def handleGetTaskOverdue(self, board_id, dateLimit = None):
        try:
            cards = self.api.get(f"boards/{board_id}/cards")
            from datetime import datetime, timezone
            if(dateLimit is not None):
                dateLimit = datetime.fromisoformat(dateLimit)
            else:
                dateLimit = datetime.now(timezone.utc)
            overdue_cards = [c for c in cards if c['due'] and not c['dueComplete'] and datetime.fromisoformat(c['due'][:-1] + '+00:00') < dateLimit]

            return [{'id': c['id'], 'name': c['name'], 'due': c['due'], 'idList': c['idList'], 'idBoard': c['idBoard'], 'dueComplete': c['dueComplete'], 'desc': c['desc'], 'idMembers': c['idMembers']} for c in overdue_cards]
                    
        except Exception as e:
            print(f"Error fetching overdue tasks: {e}")
            return None
    
    # Comments on cards
    def handleGetCommentsForCard(self, card_id):
        try:
            actions = self.api.get(f"cards/{card_id}/actions", params={'filter': 'commentCard'})
            comments = [a for a in actions if a['type'] == 'commentCard']
            return [{'id': c['id'], 'data': c['data'], 'memberCreator': c['memberCreator'], 'date': c['date']} for c in comments]
                    
        except Exception as e:
            print(f"Error fetching comments: {e}")
            return None
    
    def handleAddCommentToCard(self, card_id, comment_text):
        try:
            payload = {'text': comment_text}
            comment = self.api.post(f"cards/{card_id}/actions/comments", data=payload)
            return {'id': comment['id'], 'data': comment['data'], 'memberCreator': comment['memberCreator'], 'date': comment['date']}
                    
        except Exception as e:
            print(f"Error adding comment: {e}")
            return None

    def handleboardGetdate(self, board_id):
        try:
            cards = self.api.get(f"boards/{board_id}/cards", params={"fields": "name,due,closed,dueComplete"})
            opencard = [c for c in cards if not c.get('closed', False)]

            return [{"id": c["id"], "name": c["name"], "due": c.get("due"), "dueComplete": c.get("dueComplete")} for c
                    in opencard]
        except Exception as e:
            print(f"Error fetching lists: {e}")
            return None