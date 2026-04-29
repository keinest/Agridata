from fastapi import APIRouter, Depends
from typing import Optional
from datetime import date
from pydantic import BaseModel
from app.api.dependencies import get_accessible_exploitation, get_current_user
from app.database import db
from app.infrastructure.models import (
    Rendement, MeteoData, Intrant, User, Exploitation
)

router = APIRouter()

class StatsResponse(BaseModel):
    total_rendements: int
    avg_rendement: Optional[float] = None
    max_rendement: Optional[float] = None
    min_rendement: Optional[float] = None
    total_cost_intrants: Optional[float] = None
    avg_humidity: Optional[float] = None
    avg_temperature: Optional[float] = None

@router.get("/exploitations/stats", response_model=StatsResponse)
async def get_exploitation_stats(
    exploitation_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user)
):
    get_accessible_exploitation(current_user, exploitation_id)

    rendements = db.query("rendements", {
        "exploitation_id": exploitation_id,
        "tenant_id": current_user.tenant_id
    })

    meteo_data = db.query("meteo_data", {
        "exploitation_id": exploitation_id,
        "tenant_id": current_user.tenant_id
    })

    intrants = db.query("intrants", {
        "exploitation_id": exploitation_id,
        "tenant_id": current_user.tenant_id
    })

    if start_date or end_date:
        if start_date:
            start_str = start_date.isoformat()
            rendements = [r for r in rendements if r["date_recolte"] >= start_str]
            meteo_data = [m for m in meteo_data if m["date_observation"] >= start_str]
            intrants = [i for i in intrants if i.get("date_application") and i["date_application"] >= start_str]
        if end_date:
            end_str = end_date.isoformat()
            rendements = [r for r in rendements if r["date_recolte"] <= end_str]
            meteo_data = [m for m in meteo_data if m["date_observation"] <= end_str]
            intrants = [i for i in intrants if i.get("date_application") and i["date_application"] <= end_str]

    total_rendements = len(rendements)
    avg_rendement = sum(r["quantity"] for r in rendements) / total_rendements if rendements else None
    max_rendement = max((r["quantity"] for r in rendements), default=None)
    min_rendement = min((r["quantity"] for r in rendements), default=None)

    total_cost_intrants = sum(i["cost"] for i in intrants if i.get("cost")) if intrants else None

    avg_humidity = sum(m["humidity"] for m in meteo_data if m.get("humidity")) / len([m for m in meteo_data if m.get("humidity")]) if any(m.get("humidity") for m in meteo_data) else None
    avg_temperature = sum(m["temperature_avg"] for m in meteo_data if m.get("temperature_avg")) / len([m for m in meteo_data if m.get("temperature_avg")]) if any(m.get("temperature_avg") for m in meteo_data) else None

    return StatsResponse(
        total_rendements=total_rendements,
        avg_rendement=avg_rendement,
        max_rendement=max_rendement,
        min_rendement=min_rendement,
        total_cost_intrants=total_cost_intrants,
        avg_humidity=avg_humidity,
        avg_temperature=avg_temperature
    )

@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user)
):
    exploitations = db.query("exploitations", {"tenant_id": current_user.tenant_id})

    if current_user.role == "agriculteur":
        exploitations = [e for e in exploitations if e["owner_id"] == current_user.id]

    dashboard_data = {
        "total_exploitations": len(exploitations),
        "exploitations": [],
    }

    for expl in exploitations:
        rendements_count = len(db.query("rendements", {"exploitation_id": expl["id"]}))
        parcelles_count = len(db.query("parcelles", {"exploitation_id": expl["id"]}))
        expl_data = {
            "id": expl["id"],
            "name": expl["name"],
            "rendements_count": rendements_count,
            "parcelles_count": parcelles_count,
        }
        dashboard_data["exploitations"].append(expl_data)

    return dashboard_data

@router.get("/health")
async def analytics_health():
    return {"status": "healthy"}
