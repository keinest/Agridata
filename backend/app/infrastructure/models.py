"""SQLAlchemy ORM Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, Enum, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class Tenant(Base):
    """Tenant model for SaaS multi-tenancy"""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    logo_url = Column(String(500))
    subscription_plan = Column(String(50), default="free")
    max_users = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    exploitations = relationship("Exploitation", back_populates="tenant", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_tenant_active", "active"),
    )


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default="agriculteur")  # admin, consultant, agriculteur
    avatar_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    active = Column(Boolean, default=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    exploitations = relationship("Exploitation", back_populates="owner", foreign_keys="Exploitation.owner_id")
    
    __table_args__ = (
        Index("idx_user_tenant_email", "tenant_id", "email"),
        Index("idx_user_tenant_role", "tenant_id", "role"),
    )


class Exploitation(Base):
    """Exploitation (Farm) model"""
    __tablename__ = "exploitations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    region = Column(String(100))
    total_area = Column(Float)
    area_unit = Column(String(20), default="hectares")
    main_crops = Column(String(500))
    description = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="exploitations")
    owner = relationship("User", back_populates="exploitations", foreign_keys=[owner_id])
    parcelles = relationship("Parcelle", back_populates="exploitation", cascade="all, delete-orphan")
    rendements = relationship("Rendement", back_populates="exploitation", cascade="all, delete-orphan")
    meteo_data = relationship("MeteoData", back_populates="exploitation", cascade="all, delete-orphan")
    intrants = relationship("Intrant", back_populates="exploitation", cascade="all, delete-orphan")
    alertes = relationship("Alerte", back_populates="exploitation", cascade="all, delete-orphan")
    rapports = relationship("Rapport", back_populates="exploitation", cascade="all, delete-orphan")
    predictions = relationship("AnalysisPrediction", back_populates="exploitation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_expl_tenant_owner", "tenant_id", "owner_id"),
    )


class Parcelle(Base):
    """Parcelle (Plot) model"""
    __tablename__ = "parcelles"
    
    id = Column(Integer, primary_key=True, index=True)
    exploitation_id = Column(Integer, ForeignKey("exploitations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    area = Column(Float)
    area_unit = Column(String(20), default="hectares")
    crop_type = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exploitation = relationship("Exploitation", back_populates="parcelles")
    rendements = relationship("Rendement", back_populates="parcelle", cascade="all, delete-orphan")
    sol_qualite = relationship("SolQualite", back_populates="parcelle", cascade="all, delete-orphan")
    intrants = relationship("Intrant", back_populates="parcelle")
    
    __table_args__ = (
        Index("idx_parc_tenant_expl", "tenant_id", "exploitation_id"),
    )


class Rendement(Base):
    """Yield/Harvest data"""
    __tablename__ = "rendements"
    
    id = Column(Integer, primary_key=True, index=True)
    parcelle_id = Column(Integer, ForeignKey("parcelles.id", ondelete="CASCADE"), nullable=False)
    exploitation_id = Column(Integer, ForeignKey("exploitations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    date_recolte = Column(Date, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), default="kg")
    crop_type = Column(String(100))
    quality_rating = Column(Integer)  # 1-5
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parcelle = relationship("Parcelle", back_populates="rendements")
    exploitation = relationship("Exploitation", back_populates="rendements")
    
    __table_args__ = (
        Index("idx_rend_tenant_date", "tenant_id", "date_recolte"),
        Index("idx_rend_parcelle_date", "parcelle_id", "date_recolte"),
    )


class MeteoData(Base):
    """Weather/Climate data"""
    __tablename__ = "donnees_meteorologiques"
    
    id = Column(Integer, primary_key=True, index=True)
    exploitation_id = Column(Integer, ForeignKey("exploitations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    date_observation = Column(Date, nullable=False)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    temperature_avg = Column(Float)
    precipitation = Column(Float)
    humidity = Column(Integer)  # 0-100
    wind_speed = Column(Float)
    pressure = Column(Float)
    source = Column(String(100), default="manual")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exploitation = relationship("Exploitation", back_populates="meteo_data")
    
    __table_args__ = (
        Index("idx_meteo_tenant_date", "tenant_id", "date_observation"),
    )


class SolQualite(Base):
    """Soil quality/analysis data"""
    __tablename__ = "qualite_sol"
    
    id = Column(Integer, primary_key=True, index=True)
    parcelle_id = Column(Integer, ForeignKey("parcelles.id", ondelete="CASCADE"), nullable=False)
    exploitation_id = Column(Integer, ForeignKey("exploitations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    date_analyse = Column(Date, nullable=False)
    ph = Column(Float)
    azote = Column(Float)
    phosphore = Column(Float)
    potassium = Column(Float)
    matiere_organique = Column(Float)
    calcium = Column(Float)
    magnesium = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parcelle = relationship("Parcelle", back_populates="sol_qualite")
    
    __table_args__ = (
        Index("idx_sol_tenant_date", "tenant_id", "date_analyse"),
    )


class Intrant(Base):
    """Inputs/Supplies (fertilizer, pesticides, etc.)"""
    __tablename__ = "intrants"
    
    id = Column(Integer, primary_key=True, index=True)
    exploitation_id = Column(Integer, ForeignKey("exploitations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    parcelle_id = Column(Integer, ForeignKey("parcelles.id", ondelete="SET NULL"))
    type = Column(String(50))  # engrais, pesticide, herbicide, fongicide, autre
    name = Column(String(255), nullable=False)
    quantity = Column(Float)
    unit = Column(String(50))
    date_application = Column(Date)
    cost = Column(Float)
    effectiveness = Column(Integer)  # 0-100
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exploitation = relationship("Exploitation", back_populates="intrants")
    parcelle = relationship("Parcelle", back_populates="intrants")
    
    __table_args__ = (
        Index("idx_intrant_tenant_date", "tenant_id", "date_application"),
    )


class Alerte(Base):
    """Alert model"""
    __tablename__ = "alertes"
    
    id = Column(Integer, primary_key=True, index=True)
    exploitation_id = Column(Integer, ForeignKey("exploitations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50))  # anomalie_rendement, meteo_extreme, sol_degrade, infestation, autre
    severity = Column(String(20), default="warning")  # info, warning, critical
    title = Column(String(255), nullable=False)
    description = Column(Text)
    threshold_value = Column(Float)
    actual_value = Column(Float)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)
    
    # Relationships
    exploitation = relationship("Exploitation", back_populates="alertes")
    
    __table_args__ = (
        Index("idx_alerte_tenant_created", "tenant_id", "created_at"),
        Index("idx_alerte_exploitation", "exploitation_id"),
    )


class Rapport(Base):
    """Report model"""
    __tablename__ = "rapports"
    
    id = Column(Integer, primary_key=True, index=True)
    exploitation_id = Column(Integer, ForeignKey("exploitations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    report_type = Column(String(50))  # mensuel, annuel, custom
    period_start = Column(Date)
    period_end = Column(Date)
    file_path = Column(String(500))
    format = Column(String(20))  # pdf, excel, html
    content = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exploitation = relationship("Exploitation", back_populates="rapports")
    
    __table_args__ = (
        Index("idx_rapport_tenant_created", "tenant_id", "created_at"),
    )


class AnalysisPrediction(Base):
    """Analysis and prediction results"""
    __tablename__ = "analyses_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    exploitation_id = Column(Integer, ForeignKey("exploitations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    parcelle_id = Column(Integer, ForeignKey("parcelles.id", ondelete="SET NULL"))
    analysis_type = Column(String(50))  # rendement_futur, optimisation_intrants, sante_sol, autre
    model_version = Column(String(50))
    input_data = Column(JSON)
    result_data = Column(JSON)
    accuracy = Column(Float)  # 0-100
    confidence = Column(Float)  # 0-100
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(Date)
    
    # Relationships
    exploitation = relationship("Exploitation", back_populates="predictions")
    
    __table_args__ = (
        Index("idx_analysis_tenant_type", "tenant_id", "analysis_type"),
    )


class AuditLog(Base):
    """Audit log for tracking changes"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100))  # CREATE, UPDATE, DELETE, READ
    entity_type = Column(String(100))
    entity_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_audit_tenant_created", "tenant_id", "created_at"),
        Index("idx_audit_entity", "entity_type", "entity_id"),
    )
