# Teams API Wrapper using Microsoft Graph
#able to read a team and a specified thread

import os
import requests
from msal import ConfidentialClientApplication
from urllib.parse import quote
import httpx

# Constantes Graph
GRAPH_BASE = "https://graph.microsoft.com/v1.0"
USE_LIVE = os.getenv("USE_LIVE", "False").lower() == "true"

def _attendees_payload(emails: list[str]) -> list[dict]:
    return [
        {
            "emailAddress": {"address": e.strip()},
            "type": "required"
        } for e in emails if e and e.strip()
    ]

class TeamsConnector:
    """
    Un connecteur pour l'API Microsoft Graph, spécifiquement pour Teams.
    Gère l'authentification OAuth2 pour obtenir un jeton d'accès.
    """

    def _get_auth_headers(self) -> dict:
        """
        Construit les en-têtes d'autorisation avec le jeton Bearer.
        """
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def create_teams_meeting(
        self,
        organizer_upn: str,
        subject: str,
        start_iso: str,
        end_iso: str,
        timezone: str = "Europe/Paris",
        attendees: list[str] | None = None,
        body_html: str | None = None,
        location_display_name: str | None = None,
        send_invitations: bool = True,   
    ) -> dict:
        event = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body_html or ""},
            "start": {"dateTime": start_iso, "timeZone": timezone},
            "end":   {"dateTime": end_iso,   "timeZone": timezone},
            "isOnlineMeeting": True,
            "onlineMeetingProvider": "teamsForBusiness",
            "responseRequested": True,   
            "importance": "high",   
            "allowNewTimeProposals": True,   
            "isReminderOn": True,   
            "responseRequested": True,  
        }
        if attendees:
            event["attendees"] = _attendees_payload(attendees)
        if location_display_name:
            event["location"] = {"displayName": location_display_name}

        
        url = f"{GRAPH_BASE}/users/{organizer_upn}/events"
        if send_invitations:
            url += "?sendInvitations=true"

        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, headers=self._get_auth_headers(), json=event)
            if r.status_code >= 400:
                raise RuntimeError(f"Create meeting failed: {r.status_code} {r.text}")
            data = r.json()
            join_url = (data.get("onlineMeeting") or {}).get("joinUrl")
            return {
                "event": {
                    "id": data.get("id"),
                    "subject": data.get("subject"),
                    "start": data.get("start"),
                    "end": data.get("end"),
                    "location": data.get("location"),
                },
                "joinUrl": join_url,
                "raw": data
            }


    





    def __init__(self, tenant_id=None, client_id=None, client_secret=None, base_url="https://graph.microsoft.com/v1.0/"):
        """
        Initialise le connecteur en chargeant la configuration depuis les variables d'environnement.
        """
        self.tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")
        self.client_id = client_id or os.getenv("AZURE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("AZURE_CLIENT_SECRET")
        self.base_url = base_url
        self.scope = ["https://graph.microsoft.com/.default"]

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError("Configuration Azure manquante: AZURE_TENANT_ID, AZURE_CLIENT_ID, ou AZURE_CLIENT_SECRET.")

        # Initialise l'application MSAL pour l'authentification
        self.app = ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
        )

    def _get_token(self) -> str:
        """
        Récupère un jeton d'accès pour l'API Graph.
        Tente d'abord de le récupérer depuis le cache, sinon en fait la demande.
        """
        result = self.app.acquire_token_silent(self.scope, account=None)
        if not result:
            result = self.app.acquire_token_for_client(scopes=self.scope)

        if "access_token" not in result:
            raise RuntimeError(f"Azure AD auth error: {result}")

        return result["access_token"]


    async def list_all_users(self, select: str | None = "id,displayName,mail,userPrincipalName",
                             filter_expr: str | None = None,
                             page_size: int = 50) -> list[dict]:
        """
        Récupère tous les utilisateurs AAD via /users avec pagination.
        - select: champs à retourner (CSV), ex: "id,displayName,mail,userPrincipalName"
        - filter_expr: filtre OData optionnel, ex: "accountEnabled eq true"
        - page_size: taille de page ($top), max conseillé 999 au plus, 50 par défaut
        """
        if not True:
            # Mode mock pour tests hors-ligne
            return [
                {"id": "user-mock-1", "displayName": "Alice Mock", "mail": "alice@example.com", "userPrincipalName": "alice@example.com"},
                {"id": "user-mock-2", "displayName": "Bob Mock", "mail": "bob@example.com", "userPrincipalName": "bob@example.com"},
            ]

        # Construire l’URL de départ
        params = [f"$top={page_size}"]
        if select:
            params.append(f"$select={select}")
        if filter_expr:
            # Encoder le filtre OData proprement
            params.append(f"$filter={quote(filter_expr, safe=' ()\"\'=<>!andornulltruefalse.,')}")
        url = f"{GRAPH_BASE}/users?{'&'.join(params)}"

        items: list[dict] = []
        headers = self._get_auth_headers()
        # Si tu utilises $count/$filter avancé, parfois ConsistencyLevel:eventual est requis
        # headers["ConsistencyLevel"] = "eventual"
        response = requests.get(f"{self.base_url}{path}", headers=headers, params=params)
        response.raise_for_status()
        return response.json() if response.content else None

        async with httpx.AsyncClient(timeout=30.0) as client:
            while url:
                r = await client.get(url, headers=headers)
                # Gestion simple des erreurs
                if r.status_code in (429, 503):
                    # Backoff très simple (hackathon-friendly)
                    await asyncio.sleep(1.0)
                    continue
                r.raise_for_status()
                data = r.json()
                items.extend(data.get("value", []))
                url = data.get("@odata.nextLink")

        return items

    
    def put(self, path, data=None):
        """
        Effectue une requête PUT vers l'API Graph.
        """
        headers = self._get_auth_headers()
        response = requests.put(f"{self.base_url}{path}", headers=headers, json=data)
        response.raise_for_status()
        return response.json() if response.content else None

    def delete(self, path, params=None):
        """
        Effectue une requête DELETE vers l'API Graph.
        """
        headers = self._get_auth_headers()
        response = requests.delete(f"{self.base_url}{path}", headers=headers, params=params)
        response.raise_for_status()
        return response.json() if response.content else None
