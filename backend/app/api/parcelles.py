from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.application.auth_service import AuthorizationService
from app.api.dependencies import (
    get_accessible_exploitation,
    get_accessible_parcelle,
    get_current_user,
)
from app.database import db
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
    current_user: User = Depends(get_current_user),
):
    filters = {"tenant_id": current_user.tenant_id}
    if exploitation_id is not None:
        get_accessible_exploitation(current_user, exploitation_id)
        filters["exploitation_id"] = exploitation_id

    parcelles_data = db.query("parcelles", filters)
    parcelles_data.sort(key=lambda x: x["name"])
    return [ParcelleResponse(**p) for p in parcelles_data]

@router.post("/", response_model=ParcelleResponse)
async def create_parcelle(
    request: ParcelleCreate,
    current_user: User = Depends(get_current_user),
):
    exploitation = get_accessible_exploitation(current_user, request.exploitation_id)

    parcelle_data = {
        "exploitation_id": exploitation.id,
        "tenant_id": current_user.tenant_id,
        "name": request.name,
        "area": request.area,
        "area_unit": request.area_unit,
        "crop_type": request.crop_type,
    }

    result = db.insert("parcelles", parcelle_data)
    return ParcelleResponse(**result)

@router.put("/{parcelle_id}", response_model=ParcelleResponse)
async def update_parcelle(
    parcelle_id: int,
    request: ParcelleUpdate,
    current_user: User = Depends(get_current_user),
):
    parcelle = get_accessible_parcelle(current_user, parcelle_id)

    updates = request.model_dump(exclude_unset=True)
    if "exploitation_id" in updates:
        exploitation = get_accessible_exploitation(current_user, updates["exploitation_id"])
        updates["exploitation_id"] = exploitation.id

    db.update("parcelles", parcelle_id, updates)
    updated = db.get_by_id("parcelles", parcelle_id)
    return ParcelleResponse(**updated)

@router.delete("/{parcelle_id}")
async def delete_parcelle(
    parcelle_id: int,
    current_user: User = Depends(get_current_user),
):
    parcelle = get_accessible_parcelle(current_user, parcelle_id)
    db.delete("parcelles", parcelle_id)
    return {"detail": "Parcelle deleted"}
