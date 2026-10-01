-- ==============================================================================
-- ThermoGrek - Database Initialization Script
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Plants Metadata
CREATE TABLE IF NOT EXISTS plants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    location VARCHAR(150),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Assets Metadata
CREATE TABLE IF NOT EXISTS assets (
    id VARCHAR(50) PRIMARY KEY,
    plant_id UUID NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    asset_type VARCHAR(50) NOT NULL CHECK (asset_type IN ('SHELL_TUBE_HE', 'COOLING_TOWER')),
    health_status VARCHAR(50) NOT NULL DEFAULT 'NORMAL' CHECK (health_status IN ('NORMAL', 'WARNING', 'CRITICAL')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    decommissioned_at TIMESTAMPTZ,
    design_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Telemetry Readings (Time-Series)
CREATE TABLE IF NOT EXISTS telemetry_readings (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    asset_id VARCHAR(50) NOT NULL REFERENCES assets(id) ON DELETE RESTRICT,
    metrics JSONB NOT NULL,
    PRIMARY KEY (asset_id, timestamp, id)
);

-- 4. Thermodynamic KPIs (Time-Series)
CREATE TABLE IF NOT EXISTS thermodynamic_kpis (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    asset_id VARCHAR(50) NOT NULL REFERENCES assets(id) ON DELETE RESTRICT,
    delta_t_c DOUBLE PRECISION,
    delta_p_bar DOUBLE PRECISION,
    heat_duty_kw DOUBLE PRECISION,
    approach_temp_c DOUBLE PRECISION,
    effectiveness_pct DOUBLE PRECISION,
    health_index_pct DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (asset_id, timestamp, id)
);

-- 5. Alarms & Events
CREATE TABLE IF NOT EXISTS alarms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cleared_at TIMESTAMPTZ,
    asset_id VARCHAR(50) NOT NULL REFERENCES assets(id) ON DELETE RESTRICT,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL')),
    alarm_code VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    trigger_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    acknowledged BOOLEAN NOT NULL DEFAULT FALSE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_telemetry_asset_time ON telemetry_readings (asset_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_kpis_asset_time ON thermodynamic_kpis (asset_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alarms_active ON alarms (asset_id, acknowledged) WHERE acknowledged = FALSE;
CREATE INDEX IF NOT EXISTS idx_assets_active ON assets (is_active) WHERE is_active = TRUE;

-- Pre-seed initial plant and our two assets
INSERT INTO plants (id, name, location)
VALUES ('00000000-0000-0000-0000-000000000001', 'Virtual Thermal Utility Plant #1', 'ThermoGrek Simulation Facility')
ON CONFLICT (id) DO NOTHING;

INSERT INTO assets (id, plant_id, name, asset_type, health_status, design_parameters)
VALUES 
(
    'HE-01',
    '00000000-0000-0000-0000-000000000001',
    'Primary Shell & Tube Heat Exchanger (Lube Oil Cooling Loop)',
    'SHELL_TUBE_HE',
    'NORMAL',
    '{"nominal_heat_duty_kw": 350.0, "nominal_flow_m3h": 25.0, "nominal_clean_delta_p_bar": 0.70}'::jsonb
),
(
    'CT-01',
    '00000000-0000-0000-0000-000000000001',
    'Induced Draft Evaporative Cooling Tower',
    'COOLING_TOWER',
    'NORMAL',
    '{"design_approach_c": 4.5, "nominal_water_flow_m3h": 25.0, "fan_nominal_rpm": 1450.0}'::jsonb
)
ON CONFLICT (id) DO NOTHING;
