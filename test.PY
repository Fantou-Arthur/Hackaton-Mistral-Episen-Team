import msal
import requests
import json
import os

AZURE_TENANT_ID="77667def-a6f0-4bb0-82dc-afb4809feff0"
AZURE_CLIENT_ID="37e6bec4-9792-47f5-a3a2-434a705f88d0"
AZURE_CLIENT_SECRET="azg8Q~aoTQwdCN90s.yDzDIp5MWFIE5-EJMEMcOh"
TEAMS_TEAM_ID="51f4a2b8-7acb-4a5b-b0dc-e9a057ec8d28"
TEAMS_CHANNEL_ID="19:c3mz_0Pt1RRv6-NWdd5V2aI2YWNJZvhFVNElwoOBW7E1@thread.tacv2"
USE_LIVE="true"

# Configuration de l'authentification MSAL
config = {
    "authority": f"https://login.microsoftonline.com/{AZURE_TENANT_ID}",
    "client_id": AZURE_CLIENT_ID,
    "client_secret": AZURE_CLIENT_SECRET,
    "scope": ["https://graph.microsoft.com/.default"]
}

# Créez une instance d'application confidentielle
app = msal.ConfidentialClientApplication(
    config["client_id"], authority=config["authority"],
    client_credential=config["client_secret"]
)

# Acquérez un jeton d'accès
result = app.acquire_token_for_client(scopes=config["scope"])

if "access_token" in result:
    token = result['access_token']

    # URL de l'API Graph pour les messages du canal sans aucun filtre ni option
    graph_endpoint = f"https://graph.microsoft.com/v1.0/teams/{TEAMS_TEAM_ID}/channels/{TEAMS_CHANNEL_ID}/messages"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(graph_endpoint, headers=headers)
        response.raise_for_status()  # Lève une erreur pour les statuts HTTP anormaux

        messages = response.json().get('value', [])

        # Affichez les détails de chaque message
        print(f"Nombre total de messages trouvés dans le canal : {len(messages)}\n")

        for i, message in enumerate(messages, 1):
            created_at = message.get('createdDateTime')
            sender_name = message.get('from', {}).get('user', {}).get('displayName', 'Nom inconnu')
            message_body = message.get('body', {}).get('content', 'Pas de contenu')

            print(f"--- Message {i} ---")
            print(f"Envoyé par : {sender_name}")
            print(f"Date : {created_at}")
            print(f"Contenu : {message_body.strip()}")

            print("\n" + "-" * 30 + "\n")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API : {e}")
        print(f"Réponse de l'API : {response.text}")

else:
    print("Erreur lors de l'obtention du jeton d'accès.")
    print(result.get("error_description") or result.get("error"))