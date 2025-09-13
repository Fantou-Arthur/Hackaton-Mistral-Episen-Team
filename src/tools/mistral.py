import os
from mistralai import Mistral

from handlers import trello_handler

class MistralAI:
    def __init__(self):
        self.model = "mistral-large-latest"
        self.trello = trello_handler.TrelloHandler()

    def get_chat_response(self, user_message: str) -> str:
        api_key = os.getenv("MISTRAL_API_KEY")
        client = Mistral(api_key=api_key)
        response = client.chat.complete(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                    
                }
            ],
            
        )
        return response.choices[0].message.content


    def getboardId(self,name: str) -> str:
        # This is a placeholder function. Replace with actual logic to fetch board ID based on project name.

        allBoards = self.trello.handleGetBoards()

        prompt = f"""
        From the provided JSON data, extract and return only the ID of the project named '{name}'. If the project is not found, return None. Do not include any additional text or explanation in your response. \n
        Here is the JSON data:
        {allBoards}"""

        return self.get_chat_response(prompt)