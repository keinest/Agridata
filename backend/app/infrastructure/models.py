"""Pydantic domain models for AgriData Platform."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Tenant(BaseModel):
    id: Optional[int] = None
    name: str
    slug: str
    logo_url: Optional[str] = None
    subscription_plan: Optional[str] = "free"
    max_users: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    active: Optional[bool] = True


class User(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "agriculteur"
    avatar_url: Optional[str] = None
    last_login: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    active: Optional[bool] = True


class Exploitation(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    owner_id: int
    name: str
    region: Optional[str] = None
    total_area: Optional[float] = None
    area_unit: Optional[str] = "hectares"
    main_crops: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    active: Optional[bool] = True


class Parcelle(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    exploitation_id: int
    name: str
    area: Optional[float] = None
    area_unit: Optional[str] = "hectares"
    crop_type: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    active: Optional[bool] = True


class Rendement(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    parcelle_id: int
    exploitation_id: int
    date_recolte: str
    quantity: float
    unit: Optional[str] = None
    crop_type: Optional[str] = None
    quality_rating: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MeteoData(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    exploitation_id: int
    date_observation: str
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    temperature_avg: Optional[float] = None
    precipitation: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    pressure: Optional[float] = None
    source: Optional[str] = "manual"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SolQualite(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    parcelle_id: int
    exploitation_id: int
    date_analyse: str
    ph: Optional[float] = None
    azote: Optional[float] = None
    phosphore: Optional[float] = None
    potassium: Optional[float] = None
    matiere_organique: Optional[float] = None
    calcium: Optional[float] = None
    magnesium: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Intrant(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    parcelle_id: int
    exploitation_id: int
    type: str
    name: str
    quantity: Optional[float] = None
    date_application: str
    cost: Optional[float] = None
    effectiveness: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Alerte(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    exploitation_id: int
    severity: Optional[str] = "warning"
    title: str
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    is_read: Optional[bool] = False
    acknowledged_at: Optional[str] = None
    created_at: Optional[str] = None


class Rapport(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    exploitation_id: int
    created_by: int
    report_type: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    file_path: Optional[str] = None
    format: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


class AnalysisPrediction(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    exploitation_id: int
    analysis_type: str
    model_version: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    result_data: Optional[Dict[str, Any]] = None
    accuracy: Optional[float] = None
    confidence: Optional[float] = None
    recommendation: Optional[str] = None
    valid_until: Optional[str] = None
    created_at: Optional[str] = None


class AuditLog(BaseModel):
    id: Optional[int] = None
    tenant_id: int
    user_id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Optional[str] = None
