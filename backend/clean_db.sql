CREATE DATABASE IF NOT EXISTS agridata_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE agridata_db;

-- Table: tenants (Multi-tenant support)
CREATE TABLE IF NOT EXISTS tenants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    logo_url VARCHAR(500),
    subscription_plan ENUM('free', 'pro', 'enterprise') DEFAULT 'free',
    max_users INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    INDEX idx_tenant_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tenant_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role ENUM('admin', 'consultant', 'agriculteur') DEFAULT 'agriculteur',
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    UNIQUE KEY unique_email_tenant (email, tenant_id),
    INDEX idx_user_tenant_role (tenant_id, role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: exploitations
CREATE TABLE IF NOT EXISTS exploitations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tenant_id INT NOT NULL,
    owner_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    total_area DECIMAL(10, 2),
    area_unit ENUM('hectares', 'acres') DEFAULT 'hectares',
    main_crops VARCHAR(500),
    description TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id),
    INDEX idx_expl_tenant_owner (tenant_id, owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: parcelles
CREATE TABLE IF NOT EXISTS parcelles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    exploitation_id INT NOT NULL,
    tenant_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    area DECIMAL(10, 2),
    area_unit ENUM('hectares', 'acres') DEFAULT 'hectares',
    crop_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (exploitation_id) REFERENCES exploitations(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    INDEX idx_parc_tenant_expl (tenant_id, exploitation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: rendements
CREATE TABLE IF NOT EXISTS rendements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parcelle_id INT NOT NULL,
    exploitation_id INT NOT NULL,
    tenant_id INT NOT NULL,
    date_recolte DATE NOT NULL,
    quantity DECIMAL(15, 2) NOT NULL,
    unit VARCHAR(50) DEFAULT 'kg',
    crop_type VARCHAR(100),
    quality_rating INT CHECK(quality_rating >= 1 AND quality_rating <= 5),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parcelle_id) REFERENCES parcelles(id) ON DELETE CASCADE,
    FOREIGN KEY (exploitation_id) REFERENCES exploitations(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    INDEX idx_rend_tenant_date (tenant_id, date_recolte),
    INDEX idx_rend_parcelle_date (parcelle_id, date_recolte)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: donnees_meteorologiques
CREATE TABLE IF NOT EXISTS donnees_meteorologiques (
    id INT PRIMARY KEY AUTO_INCREMENT,
    exploitation_id INT NOT NULL,
    tenant_id INT NOT NULL,
    date_observation DATE NOT NULL,
    temperature_min DECIMAL(5, 2),
    temperature_max DECIMAL(5, 2),
    temperature_avg DECIMAL(5, 2),
    precipitation DECIMAL(8, 2),
    humidity INT CHECK(humidity >= 0 AND humidity <= 100),
    wind_speed DECIMAL(5, 2),
    pressure DECIMAL(7, 2),
    source VARCHAR(100) DEFAULT 'manual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (exploitation_id) REFERENCES exploitations(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    INDEX idx_meteo_tenant_date (tenant_id, date_observation),
    UNIQUE KEY unique_exploitation_date (exploitation_id, date_observation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: qualite_sol
CREATE TABLE IF NOT EXISTS qualite_sol (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parcelle_id INT NOT NULL,
    exploitation_id INT NOT NULL,
    tenant_id INT NOT NULL,
    date_analyse DATE NOT NULL,
    ph DECIMAL(4, 2),
    azote DECIMAL(8, 2),
    phosphore DECIMAL(8, 2),
    potassium DECIMAL(8, 2),
    matiere_organique DECIMAL(5, 2),
    calcium DECIMAL(8, 2),
    magnesium DECIMAL(8, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parcelle_id) REFERENCES parcelles(id) ON DELETE CASCADE,
    FOREIGN KEY (exploitation_id) REFERENCES exploitations(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    INDEX idx_sol_tenant_date (tenant_id, date_analyse)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: intrants
CREATE TABLE IF NOT EXISTS intrants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    exploitation_id INT NOT NULL,
    tenant_id INT NOT NULL,
    parcelle_id INT,
    type ENUM('engrais', 'pesticide', 'herbicide', 'fongicide', 'autre'),
    name VARCHAR(255) NOT NULL,
    quantity DECIMAL(15, 2),
    unit VARCHAR(50),
    date_application DATE,
    cost DECIMAL(10, 2),
    effectiveness INT CHECK(effectiveness >= 0 AND effectiveness <= 100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (exploitation_id) REFERENCES exploitations(id) ON DELETE CASCADE,
    FOREIGN KEY (parcelle_id) REFERENCES parcelles(id) ON DELETE SET NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    INDEX idx_intrant_tenant_date (tenant_id, date_application)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: alertes
CREATE TABLE IF NOT EXISTS alertes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    exploitation_id INT NOT NULL,
    tenant_id INT NOT NULL,
    type ENUM('anomalie_rendement', 'meteo_extreme', 'sol_degrade', 'infestation', 'autre'),
    severity ENUM('info', 'warning', 'critical') DEFAULT 'warning',
    title VARCHAR(255) NOT NULL,
    description TEXT,
    threshold_value DECIMAL(10, 2),
    actual_value DECIMAL(10, 2),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP NULL,
    FOREIGN KEY (exploitation_id) REFERENCES exploitations(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    INDEX idx_alerte_tenant_created (tenant_id, created_at),
    INDEX idx_alerte_exploitation (exploitation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: rapports
CREATE TABLE IF NOT EXISTS rapports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    exploitation_id INT NOT NULL,
    tenant_id INT NOT NULL,
    created_by INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    report_type ENUM('mensuel', 'annuel', 'custom'),
    period_start DATE,
    period_end DATE,
    file_path VARCHAR(500),
    format ENUM('pdf', 'excel', 'html'),
    content JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exploitation_id) REFERENCES exploitations(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_rapport_tenant_created (tenant_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: analyses_predictions
CREATE TABLE IF NOT EXISTS analyses_predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    exploitation_id INT NOT NULL,
    tenant_id INT NOT NULL,
    parcelle_id INT,
    analysis_type ENUM('rendement_futur', 'optimisation_intrants', 'sante_sol', 'autre'),
    model_version VARCHAR(50),
    input_data JSON,
    result_data JSON,
    accuracy DECIMAL(5, 2),
    confidence DECIMAL(5, 2),
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until DATE,
    FOREIGN KEY (exploitation_id) REFERENCES exploitations(id) ON DELETE CASCADE,
    FOREIGN KEY (parcelle_id) REFERENCES parcelles(id) ON DELETE SET NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    INDEX idx_analysis_tenant_type (tenant_id, analysis_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tenant_id INT NOT NULL,
    user_id INT,
    action VARCHAR(100),
    entity_type VARCHAR(100),
    entity_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_tenant_created (tenant_id, created_at),
    INDEX idx_audit_entity (entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample tenant
INSERT INTO tenants (name, slug, subscription_plan) VALUES 
('Demo Tenant', 'demo-tenant', 'pro');

-- Insert sample user
INSERT INTO users (tenant_id, email, password_hash, first_name, last_name, role) VALUES
(1, 'admin@agridata.app', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lm', 'Admin', 'User', 'admin');

COMMIT;
