import os
import httpx

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
USE_LIVE = os.getenv("USE_LIVE", "false").lower() == "true"

async def unread_mentions():
    """Retourne le nombre de messages non lus et de mentions Slack."""
    if not USE_LIVE:
        # --- Mock mode ---
        return "Slack (mock) → 3 mentions non lues, 5 messages non lus."

    url = "https://slack.com/api/conversations.history"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}

    # Pour simplifier, on prend le channel général (à remplacer par ton channel ID)
    channel_id = os.getenv("SLACK_CHANNEL_ID", "C1234567890")
    params = {"channel": channel_id, "limit": 20}

    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, params=params)
        data = r.json()

    if not data.get("ok"):
        return f"Erreur Slack API: {data}"

    messages = data.get("messages", [])
    mentions = [m for m in messages if "<@" in m.get("text", "")]
    return f"Slack → {len(mentions)} mentions récentes, {len(messages)} messages récupérés."
