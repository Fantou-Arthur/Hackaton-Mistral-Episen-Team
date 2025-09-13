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
        Récupère un résumé des messages et des mentions dans un canal pour les X dernières heures.

        Args:
            hours (int): Le nombre d'heures à rechercher (par défaut à 24).
        """
        if not self.use_live:
            return self._format_response("Teams (mock) → 42 messages récents, 5 mentions (@).")

        try:
            self._check_config()

            # Calcule le point de départ pour le filtre de temps
            start_time = datetime.now(timezone.utc) - timedelta(hours=hours)

            path = f"teams/{self.team_id}/channels/{self.channel_id}/messages"
            params = {
                "$top": "50"  # Récupère les 50 messages les plus récents
            }

            data = self.api.get(path, params=params)

            values = data.get("value", [])

            # Filtre localement les messages par date de création
            recent_messages = [
                msg for msg in values
                if datetime.fromisoformat(msg.get("createdDateTime").replace("Z", "+00:00")) >= start_time
            ]

            total_messages = len(recent_messages)
            mentions = sum(len(msg.get("mentions", [])) for msg in recent_messages if msg.get("mentions"))

            # Créer le résumé des messages pour inclure le contenu
            summary_parts = [
                f"Teams → {total_messages} messages dans les {hours} dernières heures, {mentions} mentions."
            ]

            if total_messages > 0:
                summary_parts.append("\n\nContenu des messages récents :")
                for i, msg in enumerate(recent_messages):
                    sender = msg.get('from', {}).get('user', {}).get('displayName', 'Inconnu')
                    content = msg.get('body', {}).get('content', 'Contenu non disponible').replace('<br>', ' ').replace(
                        '\n', ' ')
                    summary_parts.append(
                        f" - Message {i + 1} de {sender} : {content[:100]}...")  # Limite à 100 caractères pour la lisibilité

            result_text = "\n".join(summary_parts)
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
