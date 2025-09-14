"""
MCP Server Template
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from dotenv import load_dotenv
from connectors.teams_connector import TeamsConnector
from handlers.teams_handler import TeamsHandler
from dateutil import parser as dtparser

  

mcp = FastMCP("EPISEN_AI_TEAM_SUPPORT", port=3000, stateless_http=True, debug=True)



env_file = os.getenv("ENV_FILE", ".env.production")
AUTH_MODE = os.getenv("AUTH_MODE", "delegueted").lower()

print(f" Loading env file: {env_file}")
load_dotenv(env_file)

@mcp.tool()
async def teams_find_team(name: str = Field(description="Nom (partiel) de l'équipe")) -> dict:
    """Retourne l'ID et infos d'une team par son nom."""
    res = await TeamsConnector.find_team_by_name(name)
    return res or {"error": f"Aucune team trouvée pour {name}"}

@mcp.tool()
async def teams_find_channel(
    team_id: str = Field(description="ID de la team"),
    name: str = Field(description="Nom (partiel) du canal")
) -> dict:
    """Retourne l'ID et infos d'un canal par son nom."""
    res = await TeamsConnector.find_channel_by_name(team_id, name)
    return res or {"error": f"Aucun canal trouvé pour {name}"}

@mcp.tool(
    title="List All Users",
    description="Retourne tous les utilisateurs Azure AD via Microsoft Graph /users (avec pagination).",
)
async def teams_list_users(
    select: str = Field(
        default="id,displayName,mail,userPrincipalName",
        description="Champs à retourner (CSV) pour $select."
    ),
    filter_expr: str | None = Field(
        default=None,
        description="Filtre OData optionnel, ex: \"accountEnabled eq true\""
    ),
    page_size: int = Field(
        default=50,
        description="Taille de page ($top)."
    )
) -> dict:
    """
    Expose la liste des utilisateurs au travers de l'outil MCP.
    Renvoie un objet {count, users}.
    """
    try:
        connector = TeamsConnector() 
        users = await connector.list_all_users(
            select=select, filter_expr=filter_expr, page_size=page_size
        )
        return {"count": len(users), "users": users}
    except Exception as e:
        return {"error": f"teams_list_users failed: {e!s}"}




def _parse_dt(s: str) -> str:
    """Convertit une date naturelle/ISO en 'YYYY-MM-DDTHH:MM:SS' (sans TZ)."""
    # On laisse le fuseau géré par 'timezone' côté Graph
    return dtparser.parse(s).replace(tzinfo=None).isoformat(timespec="seconds")

@mcp.tool(
    title="Planifier une réunion Teams",
    description="Crée un événement calendrier avec lien Teams et invite des participants."
)
async def schedule_teams_meeting(
    organizer_upn: str = Field(description="UPN de l'organisateur (compte qui s'authentifie)"),
    subject: str = Field(description="Sujet de la réunion"),
    start: str = Field(description="Début (ex: '2025-09-14 14:00' ou ISO 8601)"),
    end: str = Field(description="Fin (ex: '2025-09-14 15:00' ou ISO 8601)"),
    timezone: str = Field(default="Europe/Paris", description="Fuseau horaire (ex: 'Europe/Paris')"),
    attendees_csv: str = Field(default="", description="Emails des invités, séparés par des virgules"),
    body_html: str = Field(default="", description="Description/agenda en HTML"),
    location: str = Field(default="", description="Texte libre du lieu (optionnel)")
) -> dict:
    """
    Retour: event.id, joinUrl, échos des champs.
    """
    try:
        conn = TeamsConnector()
        start_iso = _parse_dt(start)
        end_iso   = _parse_dt(end)
        attendees = [x.strip() for x in attendees_csv.split(",")] if attendees_csv else []

        res = await conn.create_teams_meeting(
            organizer_upn=organizer_upn,
            subject=subject,
            start_iso=start_iso,
            end_iso=end_iso,
            timezone=timezone,
            attendees=attendees,
            body_html=body_html,
            location_display_name=(location or None),
        )
        return {
            "status": "created",
            "eventId": res["event"]["id"],
            "subject": subject,
            "start": res["event"]["start"],
            "end": res["event"]["end"],
            "joinUrl": res["joinUrl"],
            "attendees": attendees,
            "timezone": timezone,
        }
    except Exception as e:
        return {"error": f"schedule_teams_meeting failed: {e}"}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")