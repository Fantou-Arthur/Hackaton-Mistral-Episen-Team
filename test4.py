import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import asyncio
from connectors.teams_connector import TeamsConnector

os.environ.setdefault("AZURE_TENANT_ID", "77667def-a6f0-4bb0-82dc-afb4809feff0")
os.environ.setdefault("AZURE_CLIENT_ID", "37e6bec4-9792-47f5-a3a2-434a705f88d0")
os.environ.setdefault("AZURE_CLIENT_SECRET", "azg8Q~aoTQwdCN90s.yDzDIp5MWFIE5-EJMEMcOh")  # ⚠️ à sécuriser
os.environ.setdefault("USE_LIVE", "True")

USER_A = "MichelFernandyEloka@IAsupportteams.onmicrosoft.com"
USER_B = "arthur.fantou@etu.u-pec.fr"



async def main():
    conn = TeamsConnector()
    print("🧵 Création / récupération du chat 1:1 …")
    chat = await conn.create_one_on_one_chat(USER_A, USER_B)
    print("   Chat ID:", chat.get("id"))

    print(" Envoi du message …")
    msg = await conn.send_chat_message(chat["id"], "<p>Hello depuis le hackathon 🚀</p>")
    print(" OK — messageId:", msg.get("id"))

  

if __name__ == "__main__":
    asyncio.run(main())
