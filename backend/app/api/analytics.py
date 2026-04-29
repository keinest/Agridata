"""Analytics and reporting endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date
from pydantic import BaseModel
from app.api.dependencies import get_accessible_exploitation, get_current_user
from app.database import get_db
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for an exploitation"""
    get_accessible_exploitation(db, current_user, exploitation_id)
    
    # Build queries with optional filters
    rendement_query = db.query(Rendement).filter(
        Rendement.exploitation_id == exploitation_id,
        Rendement.tenant_id == current_user.tenant_id
    )
    
    meteo_query = db.query(MeteoData).filter(
        MeteoData.exploitation_id == exploitation_id,
        MeteoData.tenant_id == current_user.tenant_id
    )
    
    intrant_query = db.query(Intrant).filter(
        Intrant.exploitation_id == exploitation_id,
        Intrant.tenant_id == current_user.tenant_id
    )
    
    if start_date:
        rendement_query = rendement_query.filter(Rendement.date_recolte >= start_date)
        meteo_query = meteo_query.filter(MeteoData.date_observation >= start_date)
        intrant_query = intrant_query.filter(Intrant.date_application >= start_date)
    
    if end_date:
        rendement_query = rendement_query.filter(Rendement.date_recolte <= end_date)
        meteo_query = meteo_query.filter(MeteoData.date_observation <= end_date)
        intrant_query = intrant_query.filter(Intrant.date_application <= end_date)
    
    # Calculate statistics
    total_rendements = rendement_query.count()
    avg_rendement = rendement_query.with_entities(func.avg(Rendement.quantity)).scalar()
    max_rendement = rendement_query.with_entities(func.max(Rendement.quantity)).scalar()
    min_rendement = rendement_query.with_entities(func.min(Rendement.quantity)).scalar()
    total_cost_intrants = intrant_query.with_entities(func.sum(Intrant.cost)).scalar()
    avg_humidity = meteo_query.with_entities(func.avg(MeteoData.humidity)).scalar()
    avg_temperature = meteo_query.with_entities(func.avg(MeteoData.temperature_avg)).scalar()
    
    return {
        "total_rendements": total_rendements,
        "avg_rendement": float(avg_rendement) if avg_rendement else None,
        "max_rendement": float(max_rendement) if max_rendement else None,
        "min_rendement": float(min_rendement) if min_rendement else None,
        "total_cost_intrants": float(total_cost_intrants) if total_cost_intrants else None,
        "avg_humidity": float(avg_humidity) if avg_humidity else None,
        "avg_temperature": float(avg_temperature) if avg_temperature else None,
    }


@router.get("/dashboard")
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard summary for all accessible exploitations"""
    
    # Get exploitations accessible to user
    query = db.query(Exploitation).filter(Exploitation.tenant_id == current_user.tenant_id)
    
    if current_user.role == "agriculteur":
        query = query.filter(Exploitation.owner_id == current_user.id)
    
    exploitations = query.all()
    
    dashboard_data = {
        "total_exploitations": len(exploitations),
        "exploitations": [],
    }
    
    for expl in exploitations:
        expl_data = {
            "id": expl.id,
            "name": expl.name,
            "rendements_count": db.query(Rendement).filter(
                Rendement.exploitation_id == expl.id
            ).count(),
            "parcelles_count": len(expl.parcelles),
        }
        dashboard_data["exploitations"].append(expl_data)
    
    return dashboard_data


@router.get("/health")
async def analytics_health():
    """Health check for analytics service"""
    return {"status": "healthy"}
