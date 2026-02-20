ALTER TABLE telemetry
  ADD COLUMN IF NOT EXISTS event_id UUID;

CREATE UNIQUE INDEX IF NOT EXISTS ux_telemetry_event_id ON telemetry(event_id);

CREATE TABLE IF NOT EXISTS edge_nodes (
  id BIGSERIAL PRIMARY KEY,
  org_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  node_id TEXT NOT NULL,
  is_online BOOLEAN NOT NULL DEFAULT TRUE,
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (org_id, node_id)
);

CREATE TABLE IF NOT EXISTS edge_command_queue (
  id BIGSERIAL PRIMARY KEY,
  org_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  node_id TEXT NOT NULL,
  command TEXT NOT NULL,
  payload JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  applied_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_edge_command_queue_pending
  ON edge_command_queue (org_id, node_id, status, created_at);

ALTER TABLE edge_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE edge_command_queue ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS edge_nodes_org_isolation ON edge_nodes;
CREATE POLICY edge_nodes_org_isolation ON edge_nodes
USING (org_id = current_setting('app.current_org_id', true)::BIGINT)
WITH CHECK (org_id = current_setting('app.current_org_id', true)::BIGINT);

DROP POLICY IF EXISTS edge_queue_org_isolation ON edge_command_queue;
CREATE POLICY edge_queue_org_isolation ON edge_command_queue
USING (org_id = current_setting('app.current_org_id', true)::BIGINT)
WITH CHECK (org_id = current_setting('app.current_org_id', true)::BIGINT);
