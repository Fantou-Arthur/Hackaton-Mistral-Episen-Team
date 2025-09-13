# Teams API Wrapper using Microsoft Graph

import os
import requests
from msal import ConfidentialClientApplication


class TeamsConnector:
    """
    Un connecteur pour l'API Microsoft Graph, spécifiquement pour Teams.
    Gère l'authentification OAuth2 pour obtenir un jeton d'accès.
    """

    

    def _get_token():
        """Récupère un access_token Graph via MSAL (application permission)."""
        app = ConfidentialClientApplication(
            CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{TENANT_ID}",
            client_credential=CLIENT_SECRET,
        )
        result = app.acquire_token_silent(GRAPH_SCOPE, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=GRAPH_SCOPE)
        if "access_token" not in result:
            raise RuntimeError(f"Azure AD auth error: {result}")
        return result["access_token"]


    def _headers():
        return {
            "Authorization": f"Bearer {_get_token()}",
            "Content-Type": "application/json"
    }

    def __init__(self, base_url="https://graph.microsoft.com/v1.0/"):
        """
        Initialise le connecteur en chargeant la configuration depuis les variables d'environnement.
        """
        # Note: Il est recommandé de charger les variables d'environnement
        # (ex: avec `from dotenv import load_dotenv; load_dotenv()`)
        # avant d'instancier ce connecteur.
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
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

    def _get_auth_headers(self) -> dict:
        """
        Construit les en-têtes d'autorisation avec le jeton Bearer.
        """
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def get(self, path, params=None):
        """
        Effectue une requête GET vers l'API Graph.
        """
        headers = self._get_auth_headers()
        response = requests.get(f"{self.base_url}{path}", headers=headers, params=params)
        response.raise_for_status()
        # Certaines réponses GET réussies peuvent ne pas avoir de corps (ex: 204 No Content)
        return response.json() if response.content else None

    def post(self, path, data=None):
        """
        Effectue une requête POST vers l'API Graph.
        Le corps de la requête (data) est envoyé en JSON.
        """
        headers = self._get_auth_headers()
        response = requests.post(f"{self.base_url}{path}", headers=headers, json=data)
        response.raise_for_status()
        return response.json() if response.content else None

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

    async def find_team_by_name(name):
        """Recherche une team par displayName."""
        if not USE_LIVE:
            return {"id": "team-mock", "displayName": name}
        teams = await _paged_collect(f"{GRAPH_BASE}/groups?$filter=resourceProvisioningOptions/Any(x:x eq 'Team')&$top=50")
        for t in teams:
            if name.lower() in (t.get("displayName") or "").lower():
                return {"id": t["id"], "displayName": t["displayName"]}
        return None


    async def find_channel_by_name(team_id, name):
        """Recherche un canal par nom dans une team donnée."""
        if not USE_LIVE:
            return {"id": "channel-mock", "displayName": name}
        chans = await _paged_collect(f"{GRAPH_BASE}/teams/{team_id}/channels")
        for c in chans:
            if name.lower() in (c.get("displayName") or "").lower():
                return {"id": c["id"], "displayName": c["displayName"]}
        return None


    async def find_user_by_email(email):
        """Recherche un utilisateur par email (UserPrincipalName)."""
        if not USE_LIVE:
            return {"id": "user-mock", "displayName": email}
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{GRAPH_BASE}/users/{email}", headers=_headers())
            if r.status_code == 200:
                u = r.json()
                return {"id": u["id"], "displayName": u.get("displayName"), "mail": u.get("mail")}
        return None