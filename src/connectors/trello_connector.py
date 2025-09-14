# Trello API Wrapper

import requests

def _attendees_payload(emails: list[str]) -> list[dict]:
    return [
        {
            "emailAddress": {"address": e.strip()},
            "type": "required"
        } for e in emails if e and e.strip()
    ]


class TrelloConnector:
    def __init__(self, api_key, token, base_url="https://api.trello.com/1/"):
        self.api_key = api_key
        self.token = token
        self.base_url = base_url

    def get(self,path, params=None):
        if params is None:
            params = {}
        params.update({
            'key': self.api_key,
            'token': self.token
        })
        response = requests.get(f"{self.base_url}{path}", params=params)
        response.raise_for_status()
        return response.json()

    def post(self,path, data=None):
        if data is None:
            data = {}
        data.update({
            'key': self.api_key,
            'token': self.token
        })
        response = requests.post(f"{self.base_url}{path}", data=data)
        response.raise_for_status()
        return response.json()
    
    def put(self,path, data=None):
        if data is None:
            data = {}
        data.update({
            'key': self.api_key,
            'token': self.token
        })
        response = requests.put(f"{self.base_url}{path}", data=data)
        response.raise_for_status()
        return response.json()
    
    def delete(self,path, params=None):
        if params is None:
            params = {}
        params.update({
            'key': self.api_key,
            'token': self.token
        })
        response = requests.delete(f"{self.base_url}{path}", params=params)
        response.raise_for_status()
        return response.json()
        