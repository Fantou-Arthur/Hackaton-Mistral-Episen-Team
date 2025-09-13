import httpx, os

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("TRELLO_BOARD_ID")
USE_LIVE = os.getenv("USE_LIVE", "false").lower() == "true"

async def sprint_summary():
    """Résumé des cartes Trello (mock ou live selon USE_LIVE)."""
    if not USE_LIVE:
        # --- Mode mock (pour hackathon/démo) ---
        return "Trello (mock) → Total: 12, Done: 5, In Progress: 4, Blocked: 3"

    url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
    params = {"key": TRELLO_KEY, "token": TRELLO_TOKEN}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        cards = r.json()

    total = len(cards)
    done = len([c for c in cards if c["idList"].lower().startswith("done")])
    blocked = len([c for c in cards if "blocked" in c["name"].lower()])

    return f"Trello → Total: {total}, Done: {done}, Blocked: {blocked}"
