# Teams API Wrapper using Microsoft Graph
#able to read a team and a specified thread

import os
import asyncio
import httpx
from msal import ConfidentialClientApplication
from urllib.parse import quote
from typing import Dict, Any, Optional, List

# Constantes Graph
GRAPH_BASE = "https://graph.microsoft.com/v1.0"
USE_LIVE = os.getenv("USE_LIVE", "False").lower() == "true"

def _attendees_payload(emails: List[str]) -> List[Dict]:
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
    Supporte les opérations synchrones et asynchrones.
    """

    def __init__(self, tenant_id: Optional[str] = None, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None, base_url: str = "https://graph.microsoft.com/v1.0/"):
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

    def _get_auth_headers(self) -> Dict[str, str]:
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
        attendees: Optional[List[str]] = None,
        body_html: Optional[str] = None,
        location_display_name: Optional[str] = None,
        send_invitations: bool = True,
    ) -> Dict[str, Any]:
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

    async def list_all_users(self, select: Optional[str] = "id,displayName,mail,userPrincipalName",
                             filter_expr: Optional[str] = None,
                             page_size: int = 50) -> List[Dict]:
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

        url = f"{self.base_url}/users?{'&'.join(params)}"
        items: List[Dict] = []
        headers = self._get_auth_headers()

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