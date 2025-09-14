import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import asyncio
from connectors.teams_connector import TeamsConnector  # adapte l'import si besoin

# --- Vars d'env (ou mets-les dans .env et charge-les avant) ---
os.environ.setdefault("AZURE_TENANT_ID", "77667def-a6f0-4bb0-82dc-afb4809feff0")
os.environ.setdefault("AZURE_CLIENT_ID", "37e6bec4-9792-47f5-a3a2-434a705f88d0")
os.environ.setdefault("AZURE_CLIENT_SECRET", "azg8Q~aoTQwdCN90s.yDzDIp5MWFIE5-EJMEMcOh")  #  à sécuriser
os.environ.setdefault("USE_LIVE", "True")

async def main():
    connector = TeamsConnector()  #  créer une instance
    users = await connector.list_all_users(
        select="id,displayName,mail,userPrincipalName",
        filter_expr=None,   # ex: "accountEnabled eq true"
        page_size=50
    )
    print(f" Users récupérés: {len(users)}")
    for i, u in enumerate(users[:5], 1):
        print(f"{i:02d}. {u.get('displayName')}  |  {u.get('userPrincipalName')}  |  {u.get('mail')}")

if __name__ == "__main__":
    asyncio.run(main())
