import os
import httpx
from msal import ConfidentialClientApplication

USE_LIVE = os.getenv("USE_LIVE", "false").lower() == "true"

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
TEAM_ID = os.getenv("TEAMS_TEAM_ID")
CHANNEL_ID = os.getenv("TEAMS_CHANNEL_ID")

GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

def _get_token() -> str:
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

async def unread_and_mentions() -> str:
    """Résumé Teams : nombre de messages récents et mentions sur un canal donné."""
    if not USE_LIVE:
        return "Teams (mock) → 42 messages récents, 5 mentions (@)."

    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, TEAM_ID, CHANNEL_ID]):
        return " Config manquante (tenant/client/secret/team/channel)."

    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{GRAPH_BASE}/teams/{TEAM_ID}/channels/{CHANNEL_ID}/messages"
    params = {"$top": "30"}  

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, headers=headers, params=params)
        if r.status_code != 200:
            return f" Graph API error {r.status_code}: {r.text}"
        data = r.json()

    values = data.get("value", [])
    total = len(values)

    mentions = 0
    for msg in values:
        if "mentions" in msg and isinstance(msg["mentions"], list):
            mentions += len(msg["mentions"])
        else:
            body = (msg.get("body") or {}).get("content") or ""
            if "<at" in body:
                mentions += body.count("<at")

    return f"Teams → {total} messages récents, {mentions} mentions."


async def send_channel_message(text: str) -> str:
    """
    Poste un message simple dans le canal TEAMS_CHANNEL_ID.
    Requiert la permission application: ChannelMessage.Send
    """
    if not USE_LIVE:
        return f"[MOCK] Message envoyé : {text}"

    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, TEAM_ID, CHANNEL_ID]):
        return " Config manquante (tenant/client/secret/team/channel)."

    headers = {
        "Authorization": f"Bearer {_get_token()}",
        "Content-Type": "application/json"
    }
    url = f"{GRAPH_BASE}/teams/{TEAM_ID}/channels/{CHANNEL_ID}/messages"
    payload = {
        "body": {
            "contentType": "html",
            "content": text  # tu peux mettre du texte ou du HTML simple
        }
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, headers=headers, json=payload)
        if r.status_code not in (200, 201):
            return f" Envoi échoué {r.status_code}: {r.text}"
    msg = r.json()
    return f" Envoyé. messageId={msg.get('id')}"

async def reply_to_message(parent_message_id: str, text: str) -> str:
    """
    Répond au message parent (thread) dans le canal.
    """
    if not USE_LIVE:
        return f"[MOCK] Réponse à {parent_message_id} : {text}"

    headers = {
        "Authorization": f"Bearer {_get_token()}",
        "Content-Type": "application/json"
    }
    url = (f"{GRAPH_BASE}/teams/{TEAM_ID}/channels/{CHANNEL_ID}"
           f"/messages/{parent_message_id}/replies")
    payload = {
        "body": {"contentType": "html", "content": text}
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, headers=headers, json=payload)
        if r.status_code not in (200, 201):
            return f" Réponse échouée {r.status_code}: {r.text}"
    msg = r.json()
    return f" Réponse envoyée. replyId={msg.get('id')}"

async def send_with_mention(user_id: str, display_name: str, text: str) -> str:
    """
    Poste un message avec mention d'un utilisateur.
    - user_id : ID Graph de l'utilisateur (GUID)
    - display_name : nom à afficher dans la mention
    """
    if not USE_LIVE:
        return f"[MOCK] @${display_name} : {text}"

    headers = {
        "Authorization": f"Bearer {_get_token()}",
        "Content-Type": "application/json"
    }
    url = f"{GRAPH_BASE}/teams/{TEAM_ID}/channels/{CHANNEL_ID}/messages"
    payload = {
        "body": {
            "contentType": "html",
            "content": f"Hello <at id='0'>{display_name}</at> — {text}"
        },
        "mentions": [
            {
                "id": 0,
                "mentionText": display_name,
                "mentioned": {
                    "user": {
                        "id": user_id  # ex: GUID de l'utilisateur
                    }
                }
            }
        ]
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, headers=headers, json=payload)
        if r.status_code not in (200, 201):
            return f" Mention échouée {r.status_code}: {r.text}"
    msg = r.json()
    return f" Envoyé avec mention. messageId={msg.get('id')}"