from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from app.api.dependencies import (
    get_accessible_exploitation,
    get_accessible_parcelle,
    get_current_user,
)
from app.database import db
from app.infrastructure.models import (
    Rendement, MeteoData, SolQualite, Intrant, User
)

router = APIRouter()

class RendementCreate(BaseModel):
    parcelle_id: int
    date_recolte: date
    quantity: float
    unit: str = "kg"
    crop_type: Optional[str] = None
    quality_rating: Optional[int] = None
    notes: Optional[str] = None

class RendementResponse(BaseModel):
    id: int
    parcelle_id: int
    exploitation_id: int
    date_recolte: date
    quantity: float
    unit: str
    crop_type: Optional[str]
    quality_rating: Optional[int]

    class Config:
        from_attributes = True

@router.post("/rendements/", response_model=RendementResponse)
async def create_rendement(
    request: RendementCreate,
    current_user: User = Depends(get_current_user)
):
    parcelle = get_accessible_parcelle(current_user, request.parcelle_id)

    rendement_data = {
        "parcelle_id": request.parcelle_id,
        "exploitation_id": parcelle.exploitation_id,
        "tenant_id": current_user.tenant_id,
        "date_recolte": request.date_recolte.isoformat(),
        "quantity": request.quantity,
        "unit": request.unit,
        "crop_type": request.crop_type,
        "quality_rating": request.quality_rating,
        "notes": request.notes,
    }

    result = db.insert("rendements", rendement_data)
    return RendementResponse(**result)

@router.get("/rendements/", response_model=List[RendementResponse])
async def list_rendements(
    parcelle_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    filters = {"tenant_id": current_user.tenant_id}
    if parcelle_id:
        filters["parcelle_id"] = parcelle_id

    rendements_data = db.query("rendements", filters)
    return [RendementResponse(**r) for r in sorted(rendements_data, key=lambda x: x["date_recolte"], reverse=True)]

@router.delete("/rendements/{rendement_id}")
async def delete_rendement(
    rendement_id: int,
    current_user: User = Depends(get_current_user)
):
    rendement_data = db.get_by_id("rendements", rendement_id)
    if not rendement_data or rendement_data.get("tenant_id") != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Rendement not found")

    get_accessible_exploitation(current_user, rendement_data["exploitation_id"])
    db.delete("rendements", rendement_id)
    return {"detail": "Rendement deleted"}

class MeteoDataCreate(BaseModel):
    exploitation_id: int
    date_observation: date
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    temperature_avg: Optional[float] = None
    precipitation: Optional[float] = None
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    pressure: Optional[float] = None

class MeteoDataResponse(BaseModel):
    id: int
    exploitation_id: int
    date_observation: date
    temperature_min: Optional[float]
    temperature_max: Optional[float]
    temperature_avg: Optional[float]
    precipitation: Optional[float]
    humidity: Optional[int]

    class Config:
        from_attributes = True

@router.post("/meteo/", response_model=MeteoDataResponse)
async def create_meteo(
    request: MeteoDataCreate,
    current_user: User = Depends(get_current_user)
):
    get_accessible_exploitation(current_user, request.exploitation_id)

    meteo_data = {
        "exploitation_id": request.exploitation_id,
        "tenant_id": current_user.tenant_id,
        "date_observation": request.date_observation.isoformat(),
        "temperature_min": request.temperature_min,
        "temperature_max": request.temperature_max,
        "temperature_avg": request.temperature_avg,
        "precipitation": request.precipitation,
        "humidity": request.humidity,
        "wind_speed": request.wind_speed,
        "pressure": request.pressure,
        "source": "manual"
    }

    result = db.insert("meteo_data", meteo_data)
    return MeteoDataResponse(**result)

@router.get("/meteo/", response_model=List[MeteoDataResponse])
async def list_meteo(
    exploitation_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    filters = {"tenant_id": current_user.tenant_id}
    if exploitation_id:
        filters["exploitation_id"] = exploitation_id

    meteo_data = db.query("meteo_data", filters)
    return [MeteoDataResponse(**m) for m in sorted(meteo_data, key=lambda x: x["date_observation"], reverse=True)]

@router.delete("/meteo/{meteo_id}")
async def delete_meteo(
    meteo_id: int,
    current_user: User = Depends(get_current_user)
):
    meteo_data = db.get_by_id("meteo_data", meteo_id)
    if not meteo_data or meteo_data.get("tenant_id") != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Meteo data not found")

    get_accessible_exploitation(current_user, meteo_data["exploitation_id"])
    db.delete("meteo_data", meteo_id)
    return {"detail": "Meteo data deleted"}

class SolQualiteCreate(BaseModel):
    parcelle_id: int
    date_analyse: date
    ph: Optional[float] = None
    azote: Optional[float] = None
    phosphore: Optional[float] = None
    potassium: Optional[float] = None
    matiere_organique: Optional[float] = None
    calcium: Optional[float] = None
    magnesium: Optional[float] = None
    notes: Optional[str] = None

class SolQualiteResponse(BaseModel):
    id: int
    parcelle_id: int
    exploitation_id: int
    date_analyse: date
    ph: Optional[float]
    azote: Optional[float]
    phosphore: Optional[float]
    potassium: Optional[float]
    matiere_organique: Optional[float]
    calcium: Optional[float]
    magnesium: Optional[float]

    class Config:
        from_attributes = True

@router.post("/sol/", response_model=SolQualiteResponse)
async def create_sol_qualite(
    request: SolQualiteCreate,
    current_user: User = Depends(get_current_user)
):
    parcelle = get_accessible_parcelle(current_user, request.parcelle_id)

    sol_data = {
        "parcelle_id": request.parcelle_id,
        "exploitation_id": parcelle.exploitation_id,
        "tenant_id": current_user.tenant_id,
        "date_analyse": request.date_analyse.isoformat(),
        "ph": request.ph,
        "azote": request.azote,
        "phosphore": request.phosphore,
        "potassium": request.potassium,
        "matiere_organique": request.matiere_organique,
        "calcium": request.calcium,
        "magnesium": request.magnesium,
        "notes": request.notes,
    }

    result = db.insert("sol_qualite", sol_data)
    return SolQualiteResponse(**result)

@router.get("/sol/", response_model=List[SolQualiteResponse])
async def list_sol_qualite(
    parcelle_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    filters = {"tenant_id": current_user.tenant_id}
    if parcelle_id:
        filters["parcelle_id"] = parcelle_id

    sol_data = db.query("sol_qualite", filters)
    return [SolQualiteResponse(**s) for s in sorted(sol_data, key=lambda x: x["date_analyse"], reverse=True)]

@router.delete("/sol/{sol_id}")
async def delete_sol_qualite(
    sol_id: int,
    current_user: User = Depends(get_current_user)
):
    sol_data = db.get_by_id("sol_qualite", sol_id)
    if not sol_data or sol_data.get("tenant_id") != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Sol data not found")

    get_accessible_exploitation(current_user, sol_data["exploitation_id"])
    db.delete("sol_qualite", sol_id)
    return {"detail": "Sol data deleted"}

class IntrantCreate(BaseModel):
    exploitation_id: int
    parcelle_id: Optional[int] = None
    type: Optional[str] = None
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    date_application: Optional[date] = None
    cost: Optional[float] = None
    effectiveness: Optional[int] = None
    notes: Optional[str] = None

class IntrantResponse(BaseModel):
    id: int
    exploitation_id: int
    parcelle_id: Optional[int]
    type: Optional[str]
    name: str
    quantity: Optional[float]
    unit: Optional[str]
    date_application: Optional[date]
    cost: Optional[float]
    effectiveness: Optional[int]

    class Config:
        from_attributes = True

@router.post("/intrants/", response_model=IntrantResponse)
async def create_intrant(
    request: IntrantCreate,
    current_user: User = Depends(get_current_user)
):
    get_accessible_exploitation(current_user, request.exploitation_id)

    intrant_data = {
        "exploitation_id": request.exploitation_id,
        "tenant_id": current_user.tenant_id,
        "parcelle_id": request.parcelle_id,
        "type": request.type,
        "name": request.name,
        "quantity": request.quantity,
        "unit": request.unit,
        "date_application": request.date_application.isoformat() if request.date_application else None,
        "cost": request.cost,
        "effectiveness": request.effectiveness,
        "notes": request.notes,
    }

    result = db.insert("intrants", intrant_data)
    return IntrantResponse(**result)

@router.get("/intrants/", response_model=List[IntrantResponse])
async def list_intrants(
    exploitation_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    filters = {"tenant_id": current_user.tenant_id}
    if exploitation_id:
        filters["exploitation_id"] = exploitation_id

    intrants_data = db.query("intrants", filters)
    return [IntrantResponse(**i) for i in sorted(intrants_data, key=lambda x: x.get("date_application") or "", reverse=True)]

@router.delete("/intrants/{intrant_id}")
async def delete_intrant(
    intrant_id: int,
    current_user: User = Depends(get_current_user)
):
    intrant_data = db.get_by_id("intrants", intrant_id)
    if not intrant_data or intrant_data.get("tenant_id") != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Intrant not found")

    get_accessible_exploitation(current_user, intrant_data["exploitation_id"])
    db.delete("intrants", intrant_id)
    return {"detail": "Intrant deleted"}
