CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS organizations (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS farms (
  id BIGSERIAL PRIMARY KEY,
  org_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  location TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS telemetry (
  ts TIMESTAMPTZ NOT NULL,
  org_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
  temp_c DOUBLE PRECISION,
  humidity_pct DOUBLE PRECISION,
  co2_ppm DOUBLE PRECISION,
  nh3_ppm DOUBLE PRECISION,
  feed_kg DOUBLE PRECISION,
  water_l DOUBLE PRECISION,
  energy_kwh DOUBLE PRECISION,
  PRIMARY KEY (ts, org_id, farm_id)
);

SELECT create_hypertable('telemetry', 'ts', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS savings_log (
  id BIGSERIAL PRIMARY KEY,
  org_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  period TEXT NOT NULL,
  documented_savings NUMERIC(14,2) NOT NULL,
  success_fee NUMERIC(14,2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE farms ENABLE ROW LEVEL SECURITY;
ALTER TABLE telemetry ENABLE ROW LEVEL SECURITY;
ALTER TABLE savings_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS farms_org_isolation ON farms;
CREATE POLICY farms_org_isolation ON farms
USING (org_id = current_setting('app.current_org_id', true)::BIGINT)
WITH CHECK (org_id = current_setting('app.current_org_id', true)::BIGINT);

DROP POLICY IF EXISTS telemetry_org_isolation ON telemetry;
CREATE POLICY telemetry_org_isolation ON telemetry
USING (org_id = current_setting('app.current_org_id', true)::BIGINT)
WITH CHECK (org_id = current_setting('app.current_org_id', true)::BIGINT);

DROP POLICY IF EXISTS savings_org_isolation ON savings_log;
CREATE POLICY savings_org_isolation ON savings_log
USING (org_id = current_setting('app.current_org_id', true)::BIGINT)
WITH CHECK (org_id = current_setting('app.current_org_id', true)::BIGINT);
