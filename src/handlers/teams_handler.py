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

    def _get_chat_id_by_user_name(self, user_name: str):
        """
        Recherche et retourne l'ID d'une discussion privée basée sur le nom d'utilisateur d'un participant.
        """
        try:
            # Requête pour obtenir toutes les discussions
            path = "me/chats"
            response_data = self.api.get(path)

            if response_data is None or 'value' not in response_data:
                return None

            chats = response_data['value']
            for chat in chats:
                # Filtrer en Python les discussions de type 'oneOnOne'
                if chat.get('chatType') == 'oneOnOne':
                    chat_id = chat.get('id')
                    members_path = f"chats/{chat_id}/members"
                    members_data = self.api.get(members_path)
                    if members_data and 'value' in members_data:
                        for member in members_data['value']:
                            if member.get('displayName') == user_name:
                                return chat_id
            return None
        except Exception as e:
            print(f"Erreur lors de la recherche de la discussion : {e}")
            return None

    def handleGetChannelMessages(self, hours: int = 24):
        """
        Récupère et affiche tous les messages d'un canal, comme dans le script d'exemple.
        """
        if not self.use_live:
            return self._format_response("Teams (mock) → Pas de contenu, mode mock actif.")

        try:
            self._check_config()
            path = f"teams/{self.team_id}/channels/{self.channel_id}/messages"
            response_data = self.api.get(path)

            if response_data is None:
                return self._format_response(
                    "L'API a renvoyé une réponse vide. Il n'y a peut-être aucun message dans le canal.")

            messages = response_data.get('value', [])
            result_parts = [f"Nombre total de messages trouvés dans le canal : {len(messages)}\n"]

            for i, message in enumerate(messages, 1):
                created_at = message.get('createdDateTime')
                message_id = message.get('id')
                sender = message.get('from')
                sender_name = 'Nom inconnu'
                if sender and sender.get('user'):
                    sender_name = sender['user'].get('displayName', 'Nom inconnu')
                message_body = message.get('body', {}).get('content', 'Pas de contenu')

                result_parts.append("--- Message {} ---".format(i))
                result_parts.append(f"ID du thread : {message_id}")
                result_parts.append("Envoyé par : {}".format(sender_name))
                result_parts.append("Date : {}".format(created_at))
                result_parts.append("Contenu : {}".format(message_body.strip()))
                result_parts.append("\n" + "-" * 30 + "\n")

            result_text = "\n".join(result_parts)
            return self._format_response(result_text)

        except Exception as e:
            print(f"Error fetching Teams messages: {e}")
            return self._format_response(f"Graph API error: {e}")

    def handleGetThreadMessages(self, parent_message_id: str):
        """
        Récupère et affiche tous les messages d'un thread.
        """
        if not self.use_live:
            return self._format_response(
                f"Teams (mock) → Pas de contenu, mode mock actif pour le thread {parent_message_id}.")

        try:
            self._check_config()
            path = f"teams/{self.team_id}/channels/{self.channel_id}/messages/{parent_message_id}/replies"
            response_data = self.api.get(path)

            if response_data is None:
                return self._format_response(
                    "L'API a renvoyé une réponse vide. Il n'y a peut-être aucune réponse dans ce thread.")

            messages = response_data.get('value', [])
            result_parts = [f"Nombre total de réponses trouvées dans le thread : {len(messages)}\n"]

            for i, message in enumerate(messages, 1):
                created_at = message.get('createdDateTime')
                sender = message.get('from')
                sender_name = 'Nom inconnu'
                if sender and sender.get('user'):
                    sender_name = sender['user'].get('displayName', 'Nom inconnu')
                message_body = message.get('body', {}).get('content', 'Pas de contenu')

                result_parts.append("--- Réponse {} ---".format(i))
                result_parts.append("Envoyé par : {}".format(sender_name))
                result_parts.append("Date : {}".format(created_at))
                result_parts.append("Contenu : {}".format(message_body.strip()))
                result_parts.append("\n" + "-" * 30 + "\n")

            result_text = "\n".join(result_parts)
            return self._format_response(result_text)

        except Exception as e:
            print(f"Error fetching Teams thread messages: {e}")
            return self._format_response(f"Graph API error: {e}")

    def handleGetPrivateMessages(self, user_name: str):
        """
        Récupère et affiche les messages d'une discussion privée avec un utilisateur spécifique.
        """
        if not self.use_live:
            return self._format_response(f"[MOCK] Messages privés avec {user_name}.")

        try:
            self._check_config()
            chat_id = self._get_chat_id_by_user_name(user_name)

            if not chat_id:
                return self._format_response(f"Aucune discussion privée trouvée avec {user_name}.")

            path = f"chats/{chat_id}/messages"
            response_data = self.api.get(path)

            if response_data is None or 'value' not in response_data:
                return self._format_response(f"L'API a renvoyé une réponse vide pour le chat avec {user_name}.")

            messages = response_data.get('value', [])
            result_parts = [f"Discussion privée avec {user_name} ({len(messages)} messages):\n"]

            for i, message in enumerate(messages, 1):
                created_at = message.get('createdDateTime')
                sender = message.get('from')
                sender_name = 'Nom inconnu'
                if sender and sender.get('user'):
                    sender_name = sender['user'].get('displayName', 'Nom inconnu')
                message_body = message.get('body', {}).get('content', 'Pas de contenu')

                result_parts.append(f"--- Message {i} ---")
                result_parts.append(f"Envoyé par : {sender_name}")
                result_parts.append(f"Date : {created_at}")
                result_parts.append(f"Contenu : {message_body.strip()}")
                result_parts.append("\n" + "-" * 30 + "\n")

            result_text = "\n".join(result_parts)
            return self._format_response(result_text)

        except Exception as e:
            print(f"Erreur lors de la récupération des messages privés : {e}")
            return self._format_response(f"Erreur de l'API Graph : {e}")

    def handleListPrivateChats(self):
        """
        Récupère et liste toutes les discussions privées de l'utilisateur.
        """
        if not self.use_live:
            return self._format_response("[MOCK] Liste des discussions privées.")

        try:
            # Requête sans filtre pour éviter les erreurs d'autorisation
            path = "me/chats"
            response_data = self.api.get(path)

            if response_data is None or 'value' not in response_data:
                return self._format_response("L'API a renvoyé une réponse vide. Aucune discussion privée trouvée.")

            chats = response_data.get('value', [])
            result_parts = ["Liste des discussions privées :\n"]

            for chat in chats:
                # Filtrer les discussions de type 'oneOnOne' en Python
                if chat.get('chatType') == 'oneOnOne':
                    chat_id = chat.get('id')
                    # Obtenez les membres de la discussion
                    members_path = f"chats/{chat_id}/members"
                    members_data = self.api.get(members_path)

                    if members_data and 'value' in members_data:
                        display_names = [member.get('displayName') for member in members_data['value']]
                        # Filtrez le nom de l'utilisateur actuel
                        display_names = [name for name in display_names if name]

                        if len(display_names) > 1:
                            partner_name = [name for name in display_names if
                                            name != os.getenv("TEAMS_USER_DISPLAY_NAME")]
                            result_parts.append(f"- ID: {chat_id}, Participants: {', '.join(partner_name)}")

            result_text = "\n".join(result_parts)
            return self._format_response(result_text)

        except Exception as e:
            print(f"Erreur lors de la liste des discussions privées : {e}")
            return self._format_response(f"Erreur de l'API Graph : {e}")

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
