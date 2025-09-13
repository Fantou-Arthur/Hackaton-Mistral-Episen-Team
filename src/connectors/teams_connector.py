import os
import json
from dotenv import load_dotenv
from connectors import teams_connector
from datetime import datetime, timedelta, timezone


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

    def handleGetChannelMessages(self, hours: int = 24):
        """
        Récupère et affiche tous les messages d'un canal, comme dans le script d'exemple.
        """
        if not self.use_live:
            return self._format_response("Teams (mock) → Pas de contenu, mode mock actif.")

        try:
            self._check_config()

            # URL de l'API Graph pour les messages du canal sans aucun filtre ni option
            path = f"teams/{self.team_id}/channels/{self.channel_id}/messages"

            data = self.api.get(path)

            if data is None:
                return self._format_response(
                    "L'API a renvoyé une réponse vide. Il n'y a peut-être aucun message dans le canal.")

            messages = data.get('value', [])
            result_parts = [f"Nombre total de messages trouvés dans le canal : {len(messages)}\n"]

            for i, message in enumerate(messages, 1):
                created_at = message.get('createdDateTime')

                # Gestion sécurisée des clés de dictionnaire imbriquées
                sender = message.get('from')
                sender_name = 'Nom inconnu'
                if sender and sender.get('user'):
                    sender_name = sender['user'].get('displayName', 'Nom inconnu')

                message_body = message.get('body', {}).get('content', 'Pas de contenu')

                result_parts.append("--- Message {} ---".format(i))
                result_parts.append("Envoyé par : {}".format(sender_name))
                result_parts.append("Date : {}".format(created_at))
                result_parts.append("Contenu : {}".format(message_body.strip()))
                result_parts.append("\n" + "-" * 30 + "\n")

            result_text = "\n".join(result_parts)
            return self._format_response(result_text)

        except Exception as e:
            print(f"Error fetching Teams messages: {e}")
            return self._format_response(f"Graph API error: {e}")

    def handleSendChannelMessage(self, text: str):
        """
        Poste un message simple dans le canal configuré.
        """
        if not self.use_live:
            return self._format_response(f"[MOCK] Message envoyé : {text}")

        try:
            self._check_config()
            path = f"teams/{self.team_id}/channels/{self.channel_id}/messages"
            payload = {"body": {"contentType": "html", "content": text}}
            msg = self.api.post(path, data=payload)
            result_text = f"Envoyé. messageId={msg.get('id')}"
            return self._format_response(result_text)
        except Exception as e:
            print(f"Error sending Teams message: {e}")
            return self._format_response(f"Envoi échoué: {e}")

    def handleReplyToMessage(self, parent_message_id: str, text: str):
        """
        Répond à un message spécifique dans un thread.
        """
        if not self.use_live:
            return self._format_response(f"[MOCK] Réponse à {parent_message_id} : {text}")

        try:
            self._check_config()
            path = f"teams/{self.team_id}/channels/{self.channel_id}/messages/{parent_message_id}/replies"
            payload = {"body": {"contentType": "html", "content": text}}
            msg = self.api.post(path, data=payload)
            result_text = f"Réponse envoyée. replyId={msg.get('id')}"
            return self._format_response(result_text)
        except Exception as e:
            print(f"Error replying to Teams message: {e}")
            return self._format_response(f"Réponse échouée: {e}")

    def handleSendWithMention(self, user_id: str, display_name: str, text: str):
        """
        Poste un message avec une mention d'un utilisateur.
        """
        if not self.use_live:
            return self._format_response(f"[MOCK] @{display_name} : {text}")

        try:
            self._check_config()
            path = f"teams/{self.team_id}/channels/{self.channel_id}/messages"
            payload = {
                "body": {
                    "contentType": "html",
                    "content": f"Bonjour <at id='0'>{display_name}</at> — {text}"
                },
                "mentions": [{
                    "id": 0,
                    "mentionText": display_name,
                    "mentioned": {"user": {"id": user_id}}
                }]
            }
            msg = self.api.post(path, data=payload)
            result_text = f"Envoyé avec mention. messageId={msg.get('id')}"
            return self._format_response(result_text)
        except Exception as e:
            print(f"Error sending mention: {e}")
            return self._format_response(f"Mention échouée: {e}")