"""Data collection endpoints for rendements, météo, sol, intrants."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from app.api.dependencies import (
    get_accessible_exploitation,
    get_accessible_parcelle,
    get_current_user,
)
from app.database import get_db
from app.infrastructure.models import (
    Rendement, MeteoData, SolQualite, Intrant, User
)

router = APIRouter()


# ========== RENDEMENT ENDPOINTS ==========

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create rendement record"""
    parcelle = get_accessible_parcelle(db, current_user, request.parcelle_id)

    rendement = Rendement(
        parcelle_id=request.parcelle_id,
        exploitation_id=parcelle.exploitation_id,
        tenant_id=current_user.tenant_id,
        date_recolte=request.date_recolte,
        quantity=request.quantity,
        unit=request.unit,
        crop_type=request.crop_type,
        quality_rating=request.quality_rating,
        notes=request.notes,
    )
    
    db.add(rendement)
    db.commit()
    db.refresh(rendement)
    
    return rendement


@router.get("/rendements/", response_model=List[RendementResponse])
async def list_rendements(
    parcelle_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List rendements"""
    query = db.query(Rendement).filter(Rendement.tenant_id == current_user.tenant_id)
    
    if parcelle_id:
        query = query.filter(Rendement.parcelle_id == parcelle_id)
    
    return query.order_by(Rendement.date_recolte.desc()).all()


@router.delete("/rendements/{rendement_id}")
async def delete_rendement(
    rendement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a rendement record."""
    rendement = db.query(Rendement).filter(
        Rendement.id == rendement_id,
        Rendement.tenant_id == current_user.tenant_id,
    ).first()

    if not rendement:
        raise HTTPException(status_code=404, detail="Rendement not found")

    get_accessible_exploitation(db, current_user, rendement.exploitation_id)
    db.delete(rendement)
    db.commit()
    return {"detail": "Rendement deleted"}


# ========== METEO ENDPOINTS ==========

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create weather data"""
    get_accessible_exploitation(db, current_user, request.exploitation_id)

    meteo = MeteoData(
        exploitation_id=request.exploitation_id,
        tenant_id=current_user.tenant_id,
        date_observation=request.date_observation,
        temperature_min=request.temperature_min,
        temperature_max=request.temperature_max,
        temperature_avg=request.temperature_avg,
        precipitation=request.precipitation,
        humidity=request.humidity,
        wind_speed=request.wind_speed,
        pressure=request.pressure,
    )
    
    db.add(meteo)
    db.commit()
    db.refresh(meteo)
    
    return meteo


@router.get("/meteo/", response_model=List[MeteoDataResponse])
async def list_meteo(
    exploitation_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List weather data"""
    query = db.query(MeteoData).filter(MeteoData.tenant_id == current_user.tenant_id)
    
    if exploitation_id:
        query = query.filter(MeteoData.exploitation_id == exploitation_id)
    
    return query.order_by(MeteoData.date_observation.desc()).all()


@router.delete("/meteo/{meteo_id}")
async def delete_meteo(
    meteo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a weather record."""
    meteo = db.query(MeteoData).filter(
        MeteoData.id == meteo_id,
        MeteoData.tenant_id == current_user.tenant_id,
    ).first()

    if not meteo:
        raise HTTPException(status_code=404, detail="Meteo data not found")

    get_accessible_exploitation(db, current_user, meteo.exploitation_id)
    db.delete(meteo)
    db.commit()
    return {"detail": "Meteo data deleted"}


# ========== SOL QUALITE ENDPOINTS ==========

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
    
    class Config:
        from_attributes = True


@router.post("/sol/", response_model=SolQualiteResponse)
async def create_sol(
    request: SolQualiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create soil quality record"""
    parcelle = get_accessible_parcelle(db, current_user, request.parcelle_id)

    sol = SolQualite(
        parcelle_id=request.parcelle_id,
        exploitation_id=parcelle.exploitation_id,
        tenant_id=current_user.tenant_id,
        date_analyse=request.date_analyse,
        ph=request.ph,
        azote=request.azote,
        phosphore=request.phosphore,
        potassium=request.potassium,
        matiere_organique=request.matiere_organique,
        calcium=request.calcium,
        magnesium=request.magnesium,
        notes=request.notes,
    )
    
    db.add(sol)
    db.commit()
    db.refresh(sol)
    
    return sol


@router.get("/sol/", response_model=List[SolQualiteResponse])
async def list_sol(
    parcelle_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List soil quality data"""
    query = db.query(SolQualite).filter(SolQualite.tenant_id == current_user.tenant_id)
    
    if parcelle_id:
        query = query.filter(SolQualite.parcelle_id == parcelle_id)
    
    return query.order_by(SolQualite.date_analyse.desc()).all()


@router.delete("/sol/{sol_id}")
async def delete_sol(
    sol_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a soil analysis record."""
    sol = db.query(SolQualite).filter(
        SolQualite.id == sol_id,
        SolQualite.tenant_id == current_user.tenant_id,
    ).first()

    if not sol:
        raise HTTPException(status_code=404, detail="Soil analysis not found")

    get_accessible_exploitation(db, current_user, sol.exploitation_id)
    db.delete(sol)
    db.commit()
    return {"detail": "Soil analysis deleted"}


# ========== INTRANTS ENDPOINTS ==========

class IntrantCreate(BaseModel):
    exploitation_id: int
    parcelle_id: Optional[int] = None
    type: str
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
    type: str
    name: str
    quantity: Optional[float]
    date_application: Optional[date]
    cost: Optional[float]
    
    class Config:
        from_attributes = True


@router.post("/intrants/", response_model=IntrantResponse)
async def create_intrant(
    request: IntrantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create intrant record"""
    get_accessible_exploitation(db, current_user, request.exploitation_id)
    if request.parcelle_id is not None:
        parcelle = get_accessible_parcelle(db, current_user, request.parcelle_id)
        if parcelle.exploitation_id != request.exploitation_id:
            raise HTTPException(
                status_code=400,
                detail="Parcelle does not belong to the selected exploitation",
            )

    intrant = Intrant(
        exploitation_id=request.exploitation_id,
        tenant_id=current_user.tenant_id,
        parcelle_id=request.parcelle_id,
        type=request.type,
        name=request.name,
        quantity=request.quantity,
        unit=request.unit,
        date_application=request.date_application,
        cost=request.cost,
        effectiveness=request.effectiveness,
        notes=request.notes,
    )
    
    db.add(intrant)
    db.commit()
    db.refresh(intrant)
    
    return intrant


@router.get("/intrants/", response_model=List[IntrantResponse])
async def list_intrants(
    exploitation_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List intrants"""
    query = db.query(Intrant).filter(Intrant.tenant_id == current_user.tenant_id)
    
    if exploitation_id:
        query = query.filter(Intrant.exploitation_id == exploitation_id)
    
    return query.order_by(Intrant.date_application.desc()).all()


@router.delete("/intrants/{intrant_id}")
async def delete_intrant(
    intrant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an intrant record."""
    intrant = db.query(Intrant).filter(
        Intrant.id == intrant_id,
        Intrant.tenant_id == current_user.tenant_id,
    ).first()

    if not intrant:
        raise HTTPException(status_code=404, detail="Intrant not found")

    get_accessible_exploitation(db, current_user, intrant.exploitation_id)
    db.delete(intrant)
    db.commit()
    return {"detail": "Intrant deleted"}
