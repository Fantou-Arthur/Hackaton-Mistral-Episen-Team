# Teams API Wrapper using Microsoft Graph
import os
import requests
from msal import ConfidentialClientApplication


class TeamsConnector:
    """
    Un connecteur pour l'API Microsoft Graph, spécifiquement pour Teams.
    Gère l'authentification OAuth2 pour obtenir un jeton d'accès.
    """

    def __init__(self, tenant_id=None, client_id=None, client_secret=None, base_url="https://graph.microsoft.com/v1.0/"):
        """
        Initialise le connecteur en chargeant la configuration depuis les variables d'environnement.
        """
        # Note: Il est recommandé de charger les variables d'environnement
        # (ex: avec `from dotenv import load_dotenv; load_dotenv()`)
        # avant d'instancier ce connecteur.
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


