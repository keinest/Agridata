"""Parcelle endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.auth_service import AuthorizationService
from app.api.dependencies import (
    get_accessible_exploitation,
    get_accessible_parcelle,
    get_current_user,
)
from app.database import get_db
from app.infrastructure.models import Parcelle, User

router = APIRouter()


class ParcelleCreate(BaseModel):
    exploitation_id: int
    name: str
    area: Optional[float] = None
    area_unit: str = "hectares"
    crop_type: Optional[str] = None


class ParcelleUpdate(BaseModel):
    exploitation_id: Optional[int] = None
    name: Optional[str] = None
    area: Optional[float] = None
    area_unit: Optional[str] = None
    crop_type: Optional[str] = None


class ParcelleResponse(BaseModel):
    id: int
    exploitation_id: int
    tenant_id: int
    name: str
    area: Optional[float]
    area_unit: str
    crop_type: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ParcelleResponse])
async def list_parcelles(
    exploitation_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List parcelles accessible to the current user."""
    query = db.query(Parcelle).filter(Parcelle.tenant_id == current_user.tenant_id)

    if exploitation_id is not None:
        get_accessible_exploitation(db, current_user, exploitation_id)
        query = query.filter(Parcelle.exploitation_id == exploitation_id)

    parcelles = [
        parcelle
        for parcelle in query.order_by(Parcelle.name.asc()).all()
        if AuthorizationService.can_access_exploitation(current_user, parcelle.exploitation)
    ]
    return parcelles


@router.post("/", response_model=ParcelleResponse)
async def create_parcelle(
    request: ParcelleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a parcelle for an accessible exploitation."""
    exploitation = get_accessible_exploitation(db, current_user, request.exploitation_id)

    parcelle = Parcelle(
        exploitation_id=exploitation.id,
        tenant_id=current_user.tenant_id,
        name=request.name,
        area=request.area,
        area_unit=request.area_unit,
        crop_type=request.crop_type,
    )
    db.add(parcelle)
    db.commit()
    db.refresh(parcelle)
    return parcelle


@router.put("/{parcelle_id}", response_model=ParcelleResponse)
async def update_parcelle(
    parcelle_id: int,
    request: ParcelleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a parcelle."""
    parcelle = get_accessible_parcelle(db, current_user, parcelle_id)

    updates = request.model_dump(exclude_unset=True)
    if "exploitation_id" in updates:
        exploitation = get_accessible_exploitation(db, current_user, updates["exploitation_id"])
        parcelle.exploitation_id = exploitation.id
        updates.pop("exploitation_id")

    for field, value in updates.items():
        setattr(parcelle, field, value)

    db.commit()
    db.refresh(parcelle)
    return parcelle


@router.delete("/{parcelle_id}")
async def delete_parcelle(
    parcelle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a parcelle."""
    parcelle = get_accessible_parcelle(db, current_user, parcelle_id)
    db.delete(parcelle)
    db.commit()
    return {"detail": "Parcelle deleted"}
