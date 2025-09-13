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
    """Récupère un token d’accès via MSAL."""
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

async def unread_and_mentions():
    """Retourne un résumé Teams : nombre de messages récents et mentions."""
    if not USE_LIVE:
        return "Teams (mock) → 42 messages récents, 5 mentions (@)."

    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, TEAM_ID, CHANNEL_ID]):
        return "⚠️ Config manquante (tenant/client/secret/team/channel)."

    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{GRAPH_BASE}/teams/{TEAM_ID}/channels/{CHANNEL_ID}/messages"
    params = {"$top": "30"}  # messages récents

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, headers=headers, params=params)
        if r.status_code != 200:
            return f"❌ Graph API error {r.status_code}: {r.text}"
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

    return f"✅ Teams → {total} messages récents, {mentions} mentions."
