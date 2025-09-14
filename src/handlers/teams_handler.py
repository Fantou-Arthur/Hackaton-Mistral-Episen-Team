import os
import json
from dotenv import load_dotenv
from connectors import teams_connector


class TeamsHandler:
    """
    Gère la logique métier pour les opérations Teams en utilisant le TeamsConnector.
    """

    def __init__(self):
        """
        Initialise le handler, charge les variables d'environnement et crée une instance du connecteur.
        """
        load_dotenv()
        self.api = teams_connector.TeamsConnector(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )
        self.team_id = os.getenv("TEAMS_TEAM_ID")
        self.channel_id = os.getenv("TEAMS_CHANNEL_ID")
        self.use_live = os.getenv("USE_LIVE", "false").lower() == "true"

    def _check_config(self):
        """Vérifie que la configuration nécessaire est présente."""
        if not all([self.api.tenant_id, self.api.client_id, self.api.client_secret, self.team_id, self.channel_id]):
            raise ValueError("Configuration manquante (tenant/client/secret/team/channel).")

    def _format_response(self, text_content):
        """Met en forme la réponse dans la structure attendue."""
        return {'content': [{'type': 'text', 'text': text_content}]}

    def handleGetUnreadAndMentions(self):
        """
        Récupère un résumé des messages récents et des mentions dans un canal.
        """
        if not self.use_live:
            return self._format_response("Teams (mock) → 42 messages récents, 5 mentions (@).")

        try:
            self._check_config()
            path = f"teams/{self.team_id}/channels/{self.channel_id}/messages"
            params = {"$top": "30"}
            data = self.api.get(path, params=params)

            values = data.get("value", [])
            total = len(values)
            mentions = sum(len(msg.get("mentions", [])) for msg in values if msg.get("mentions"))

            result_text = f"Teams → {total} messages récents, {mentions} mentions."
            return self._format_response(result_text)
        except Exception as e:
            print(f"Error fetching Teams messages: {e}")
            return self._format_response(f"Graph API error: {e}")
