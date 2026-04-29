from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class Tenant(BaseModel):
    id: int
    name: str
    slug: str
    logo_url: Optional[str] = None
    subscription_plan: str = "free"
    max_users: int = 10
    created_at: str
    updated_at: str
    active: bool = True

class User(BaseModel):
    id: int
    tenant_id: int
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "agriculteur"
    avatar_url: Optional[str] = None
    created_at: str
    updated_at: str
    last_login: Optional[str] = None
    active: bool = True

class Exploitation(BaseModel):
    id: int
    tenant_id: int
    owner_id: int
    name: str
    region: Optional[str] = None
    total_area: Optional[float] = None
    area_unit: str = "hectares"
    main_crops: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: str
    updated_at: str

class Parcelle(BaseModel):
    id: int
    exploitation_id: int
    tenant_id: int
    name: str
    area: Optional[float] = None
    area_unit: str = "hectares"
    crop_type: Optional[str] = None
    created_at: str
    updated_at: str

class Rendement(BaseModel):
    id: int
    parcelle_id: int
    exploitation_id: int
    tenant_id: int
    date_recolte: str
    quantity: float
    unit: str = "kg"
    crop_type: Optional[str] = None
    quality_rating: Optional[int] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str

class MeteoData(BaseModel):
    id: int
    exploitation_id: int
    tenant_id: int
    date_observation: str
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    temperature_avg: Optional[float] = None
    precipitation: Optional[float] = None
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    pressure: Optional[float] = None
    source: str = "manual"
    created_at: str
    updated_at: str

class SolQualite(BaseModel):
    id: int
    parcelle_id: int
    exploitation_id: int
    tenant_id: int
    date_analyse: str
    ph: Optional[float] = None
    azote: Optional[float] = None
    phosphore: Optional[float] = None
    potassium: Optional[float] = None
    matiere_organique: Optional[float] = None
    calcium: Optional[float] = None
    magnesium: Optional[float] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str

class Intrant(BaseModel):
    id: int
    exploitation_id: int
    tenant_id: int
    parcelle_id: Optional[int] = None
    type: Optional[str] = None
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    date_application: Optional[str] = None
    cost: Optional[float] = None
    effectiveness: Optional[int] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str

class Alerte(BaseModel):
    id: int
    exploitation_id: int
    tenant_id: int
    type: Optional[str] = None
    severity: str = "warning"
    title: str
    description: Optional[str] = None
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    is_read: bool = False
    created_at: str
    acknowledged_at: Optional[str] = None

class Rapport(BaseModel):
    id: int
    exploitation_id: int
    tenant_id: int
    created_by: Optional[int] = None
    title: str
    report_type: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    file_path: Optional[str] = None
    format: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    created_at: str

class AnalysisPrediction(BaseModel):
    id: int
    exploitation_id: int
    tenant_id: int
    parcelle_id: Optional[int] = None
    analysis_type: Optional[str] = None
    model_version: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    result_data: Optional[Dict[str, Any]] = None
    accuracy: Optional[float] = None
    confidence: Optional[float] = None
    recommendation: Optional[str] = None
    created_at: str
    valid_until: Optional[str] = None

class AuditLog(BaseModel):
    id: int
    tenant_id: int
    user_id: Optional[int] = None
    action: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: str
