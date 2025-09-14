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
        self.user_id = os.getenv("TEAMS_USER_ID")
        self.use_live = os.getenv("USE_LIVE", "false").lower() == "true"

    def _check_config(self):
        """Vérifie que la configuration nécessaire est présente."""
        if not all([self.api.tenant_id, self.api.client_id, self.api.client_secret, self.team_id, self.channel_id]):
            raise ValueError("Configuration manquante (tenant/client/secret/team/channel).")

    def _format_response(self, text_content):
        """Met en forme la réponse dans la structure attendue."""
        return {'content': [{'type': 'text', 'text': text_content}]}

    def handleListTeamMembers(self):
        """
        Récupère et liste tous les membres de l'équipe.
        """
        if not self.use_live:
            return self._format_response("Teams (mock) → Liste des membres, mode mock actif.")

        try:
            self._check_config()
            path = f"teams/{self.team_id}/members"
            response_data = self.api.get(path)

            if response_data is None or 'value' not in response_data:
                return self._format_response("L'API a renvoyé une réponse vide. Aucun membre trouvé.")

            members = response_data.get('value', [])
            result_parts = [f"Nombre total de membres trouvés : {len(members)}\n"]

            for i, member in enumerate(members, 1):
                user_id = member.get('userId')
                display_name = member.get('displayName', 'Nom inconnu')
                result_parts.append(f"- Membre {i}: {display_name} (ID: {user_id})")

            result_text = "\n".join(result_parts)
            return self._format_response(result_text)

        except Exception as e:
            print(f"Erreur lors de la récupération des membres de l'équipe: {e}")
            return self._format_response(f"Erreur de l'API Graph: {e}")

    def handleListPrivateChats(self):
        """
        Récupère et liste toutes les discussions privées de l'utilisateur.
        """
        if not self.use_live:
            return self._format_response("[MOCK] Liste des discussions privées.")

        try:
            # Vérification si l'ID utilisateur est disponible
            if not self.user_id:
                raise ValueError("Configuration manquante: TEAMS_USER_ID.")

            # Correction de l'URL de l'API : utiliser /users/{user-id}/chats au lieu de /me/chats
            path = f"users/{self.user_id}/chats?$filter=chatType eq 'oneOnOne'"
            response_data = self.api.get(path)

            if response_data is None or 'value' not in response_data:
                return self._format_response("L'API a renvoyé une réponse vide. Aucune discussion privée trouvée.")

            chats = response_data.get('value', [])
            result_parts = ["Liste des discussions privées :\n"]

            for chat in chats:
                chat_id = chat.get('id')
                members_path = f"chats/{chat_id}/members"
                members_data = self.api.get(members_path)

                if members_data and 'value' in members_data:
                    display_names = [member.get('displayName') for member in members_data['value']]
                    # Filtrez le nom de l'utilisateur actuel
                    display_names = [name for name in display_names if name]

                    # On affiche seulement l'autre participant
                    partner_names = [name for name in display_names if name != os.getenv("TEAMS_USER_DISPLAY_NAME")]

                    if partner_names:
                        result_parts.append(f"- ID: {chat_id}, Participants: {', '.join(partner_names)}")

            result_text = "\n".join(result_parts)
            return self._format_response(result_text)

        except Exception as e:
            print(f"Erreur lors de la liste des discussions privées : {e}")
            return self._format_response(f"Erreur de l'API Graph : {e}")

    def handleGetPrivateMessages(self, chat_id: str):
        """
        Récupère les messages d'un chat privé donné son ID.
        """
        if not self.use_live:
            return self._format_response(f"[MOCK] Messages du chat privé {chat_id}.")

        try:
            path = f"chats/{chat_id}/messages"
            response_data = self.api.get(path)

            if response_data is None or 'value' not in response_data:
                return self._format_response("L'API a renvoyé une réponse vide. Aucun message trouvé.")

            messages = response_data.get('value', [])
            result_parts = [f"Messages du chat ID {chat_id}:\n"]

            for i, message in enumerate(messages, 1):
                sender = message.get('from')
                sender_name = 'Nom inconnu'
                if sender and sender.get('user'):
                    sender_name = sender['user'].get('displayName', 'Nom inconnu')
                message_body = message.get('body', {}).get('content', 'Pas de contenu')
                created_at = message.get('createdDateTime')

                result_parts.append("--- Message {} ---".format(i))
                result_parts.append("Envoyé par : {}".format(sender_name))
                result_parts.append("Date : {}".format(created_at))
                result_parts.append("Contenu : {}".format(message_body.strip()))
                result_parts.append("\n" + "-" * 30 + "\n")

            result_text = "\n".join(result_parts)
            return self._format_response(result_text)

        except Exception as e:
            print(f"Erreur lors de la récupération des messages privés : {e}")
            return self._format_response(f"Erreur de l'API Graph : {e}")


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
