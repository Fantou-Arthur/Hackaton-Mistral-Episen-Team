import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import asyncio
from datetime import datetime, timedelta

from connectors.teams_connector import TeamsConnector
os.environ["AZURE_TENANT_ID"] = "77667def-a6f0-4bb0-82dc-afb4809feff0"
os.environ["AZURE_CLIENT_ID"] = "37e6bec4-9792-47f5-a3a2-434a705f88d0"
os.environ["AZURE_CLIENT_SECRET"] = "azg8Q~aoTQwdCN90s.yDzDIp5MWFIE5-EJMEMcOh"   # <-- Mets ton vrai secret ici
os.environ["USE_LIVE"] = "True"
# ⚠️ Mets ton propre UPN (adresse mail) qui a un calendrier dans ton tenant
ORGANIZER = "MichelFernandyEloka@IAsupportteams.onmicrosoft.com"
ATTENDEES = ["arthur.fantou@etu.u-pec.fr"]

async def main():
    conn = TeamsConnector()

    print("📅 Création d'une réunion Teams...")

    start = datetime(2025, 9, 15, 14, 0, 0).strftime("%Y-%m-%dT%H:%M:%S")
    end   = datetime(2025, 9, 15, 14, 30, 0).strftime("%Y-%m-%dT%H:%M:%S")

    meeting = await conn.create_teams_meeting(
        organizer_upn=ORGANIZER,
        subject="Réunion test Hackathon 🚀",
        start_iso=start,
        end_iso=end,
        timezone="Europe/Paris",
        attendees=ATTENDEES,
        body_html="<p>Test d'une réunion Teams créée via Graph API</p>",
        location_display_name="En ligne",
        send_invitations=True, 
    )

    print("✅ Réunion créée :")
    print(f"- Sujet: {meeting['event']['subject']}")
    print(f"- Début: {meeting['event']['start']}")
    print(f"- Fin:   {meeting['event']['end']}")
    print(f"- Lien Teams: {meeting['joinUrl']}")

if __name__ == "__main__":
    asyncio.run(main())
