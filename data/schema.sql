-- Consultant Pulse tables from docs/design.md.
-- Edit the catalog and schema, then run this whole script in Databricks SQL.
-- This workspace uses catalog workspace.
-- Dev schema: michael_woodward. Prod schema: consultant_pulse.

USE CATALOG workspace;
CREATE SCHEMA IF NOT EXISTS consultant_pulse
COMMENT 'Consultant Pulse tables';
USE SCHEMA consultant_pulse;

CREATE TABLE IF NOT EXISTS consultants (
  consultant_id STRING NOT NULL COMMENT 'Primary logical key',
  name STRING NOT NULL,
  email STRING NOT NULL,
  role STRING,
  manager_id STRING,
  active_flag BOOLEAN NOT NULL,
  created_timestamp TIMESTAMP NOT NULL,
  updated_timestamp TIMESTAMP NOT NULL
)
USING DELTA
CLUSTER BY (consultant_id)
COMMENT 'Consultants';

CREATE TABLE IF NOT EXISTS projects (
  project_id STRING NOT NULL COMMENT 'Primary logical key',
  project_name STRING NOT NULL,
  customer STRING NOT NULL,
  tpm_name STRING,
  tpm_email STRING,
  start_date DATE,
  end_date DATE,
  status STRING,
  created_timestamp TIMESTAMP NOT NULL,
  updated_timestamp TIMESTAMP NOT NULL
)
USING DELTA
CLUSTER BY (project_id)
COMMENT 'Projects';

CREATE TABLE IF NOT EXISTS project_assignments (
  consultant_id STRING NOT NULL,
  project_id STRING NOT NULL,
  assignment_role STRING,
  start_date DATE,
  end_date DATE,
  active_flag BOOLEAN NOT NULL
)
USING DELTA
CLUSTER BY (consultant_id, project_id)
COMMENT 'Which consultants worked on which projects';

CREATE TABLE IF NOT EXISTS competencies (
  competency_id STRING NOT NULL COMMENT 'Primary logical key',
  competency_name STRING NOT NULL,
  description STRING,
  display_order INT NOT NULL,
  active_flag BOOLEAN NOT NULL
)
USING DELTA
CLUSTER BY (competency_id)
COMMENT 'Competency definitions';

CREATE TABLE IF NOT EXISTS feedback (
  feedback_id STRING NOT NULL COMMENT 'Primary logical key',
  consultant_id STRING NOT NULL,
  project_id STRING NOT NULL,
  submitted_by_name STRING NOT NULL,
  submitted_by_email STRING NOT NULL,
  submitted_timestamp TIMESTAMP NOT NULL,
  feedback_type STRING NOT NULL COMMENT 'STRENGTH, DEVELOPMENT_OPPORTUNITY, RECOGNITION, CONCERN',
  competency_id STRING NOT NULL,
  observation STRING NOT NULL,
  impact STRING NOT NULL,
  development_opportunity STRING,
  follow_up_required BOOLEAN NOT NULL,
  visibility STRING NOT NULL COMMENT 'MANAGER_ONLY, MANAGER_AND_CONSULTANT',
  created_timestamp TIMESTAMP NOT NULL,
  updated_timestamp TIMESTAMP NOT NULL
)
USING DELTA
CLUSTER BY (consultant_id, submitted_timestamp)
COMMENT 'Documented observations. No numeric performance rating.';

MERGE INTO consultants AS target
USING (
  SELECT 'taylor-brown' AS consultant_id, 'Taylor Brown' AS name, 'taylor.brown@example.com' AS email,
    'Manager' AS role, CAST(NULL AS STRING) AS manager_id, true AS active_flag,
    TIMESTAMP '2026-01-06 00:00:00' AS created_timestamp, TIMESTAMP '2026-01-06 00:00:00' AS updated_timestamp
  UNION ALL
  SELECT 'alex-morgan', 'Alex Morgan', 'alex.morgan@example.com',
    'Senior Consultant', 'taylor-brown', true,
    TIMESTAMP '2026-01-06 00:00:00', TIMESTAMP '2026-01-06 00:00:00'
  UNION ALL
  SELECT 'chris-davis', 'Chris Davis', 'chris.davis@example.com',
    'Consultant', 'taylor-brown', true,
    TIMESTAMP '2026-01-06 00:00:00', TIMESTAMP '2026-01-06 00:00:00'
  UNION ALL
  SELECT 'jamie-wilson', 'Jamie Wilson', 'jamie.wilson@example.com',
    'Consultant', 'taylor-brown', true,
    TIMESTAMP '2026-01-06 00:00:00', TIMESTAMP '2026-01-06 00:00:00'
) AS source
ON target.consultant_id = source.consultant_id
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO projects AS target
USING (
  SELECT 'project-abc' AS project_id, 'Customer ABC platform' AS project_name, 'Customer ABC' AS customer,
    'Jordan Lee' AS tpm_name, 'jordan.lee@example.com' AS tpm_email,
    DATE '2026-01-06' AS start_date, DATE '2026-06-30' AS end_date, 'Active' AS status,
    TIMESTAMP '2026-01-06 00:00:00' AS created_timestamp, TIMESTAMP '2026-01-06 00:00:00' AS updated_timestamp
  UNION ALL
  SELECT 'project-xyz', 'Customer XYZ migration', 'Customer XYZ',
    'Jordan Lee', 'jordan.lee@example.com',
    DATE '2026-02-02', DATE '2026-08-31', 'Active',
    TIMESTAMP '2026-02-02 00:00:00', TIMESTAMP '2026-02-02 00:00:00'
  UNION ALL
  SELECT 'project-123', 'Customer 123 analytics', 'Customer 123',
    'Sam Patel', 'sam.patel@example.com',
    DATE '2026-03-02', CAST(NULL AS DATE), 'Active',
    TIMESTAMP '2026-03-02 00:00:00', TIMESTAMP '2026-03-02 00:00:00'
) AS source
ON target.project_id = source.project_id
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO project_assignments AS target
USING (
  SELECT 'alex-morgan' AS consultant_id, 'project-abc' AS project_id, 'Data Engineer' AS assignment_role,
    DATE '2026-01-06' AS start_date, DATE '2026-06-30' AS end_date, true AS active_flag
  UNION ALL
  SELECT 'alex-morgan', 'project-xyz', 'Data Engineer', DATE '2026-02-02', DATE '2026-08-31', true
  UNION ALL
  SELECT 'chris-davis', 'project-abc', 'Analytics Engineer', DATE '2026-01-06', DATE '2026-06-30', true
  UNION ALL
  SELECT 'jamie-wilson', 'project-xyz', 'Consultant', DATE '2026-02-02', DATE '2026-08-31', true
  UNION ALL
  SELECT 'jamie-wilson', 'project-123', 'Consultant', DATE '2026-03-02', CAST(NULL AS DATE), true
) AS source
ON target.consultant_id = source.consultant_id AND target.project_id = source.project_id
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO competencies AS target
USING (
  SELECT 'TECHNICAL_EXPERTISE' AS competency_id, 'Technical Expertise' AS competency_name,
    'Specific technical work on architecture, implementation, or troubleshooting.' AS description,
    1 AS display_order, true AS active_flag
  UNION ALL
  SELECT 'CUSTOMER_IMPACT', 'Customer Impact',
    'Effect on the customer outcome, experience, or decision.', 2, true
  UNION ALL
  SELECT 'DELIVERY_EXECUTION', 'Delivery / Execution',
    'Progress against scope, schedule, quality, or a delivery commitment.', 3, true
  UNION ALL
  SELECT 'COMMUNICATION', 'Communication',
    'How clearly the consultant explained, wrote, or presented.', 4, true
  UNION ALL
  SELECT 'COLLABORATION', 'Collaboration',
    'How the consultant worked with the customer team or the delivery team.', 5, true
  UNION ALL
  SELECT 'OWNERSHIP', 'Ownership',
    'Where the consultant took responsibility for an outcome.', 6, true
  UNION ALL
  SELECT 'LEADERSHIP', 'Leadership',
    'Where the consultant guided other people or a decision.', 7, true
  UNION ALL
  SELECT 'DATABRICKS_EXPERTISE', 'Databricks Expertise',
    'Use of Databricks products, patterns, or platform capabilities.', 8, true
  UNION ALL
  SELECT 'BUSINESS_ACUMEN', 'Business Acumen',
    'Connection between the technical work and the business outcome.', 9, true
) AS source
ON target.competency_id = source.competency_id
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO feedback AS target
USING (
  SELECT
    'seed-feedback-0001' AS feedback_id,
    'alex-morgan' AS consultant_id,
    'project-abc' AS project_id,
    'Jordan Lee' AS submitted_by_name,
    'jordan.lee@example.com' AS submitted_by_email,
    TIMESTAMP '2026-09-18 15:00:00' AS submitted_timestamp,
    'STRENGTH' AS feedback_type,
    'TECHNICAL_EXPERTISE' AS competency_id,
    'Alex took ownership of the customer streaming architecture when the original design was missing its latency target.' AS observation,
    'Alex worked with the customer engineering team to redesign the pipeline and helped return the project to schedule.' AS impact,
    CAST(NULL AS STRING) AS development_opportunity,
    false AS follow_up_required,
    'MANAGER_ONLY' AS visibility,
    TIMESTAMP '2026-09-18 15:00:00' AS created_timestamp,
    TIMESTAMP '2026-09-18 15:00:00' AS updated_timestamp
  UNION ALL
  SELECT
    'seed-feedback-0002',
    'alex-morgan',
    'project-xyz',
    'Jordan Lee',
    'jordan.lee@example.com',
    TIMESTAMP '2026-08-27 15:00:00',
    'DEVELOPMENT_OPPORTUNITY',
    'COMMUNICATION',
    'Alex completed the migration cutover checklist but sent the status note to the delivery team after the customer steering meeting.',
    'The customer heard the cutover result from their own team first, and the steering meeting spent time reconstructing the timeline.',
    'Send the customer status note before the steering meeting when a cutover decision is on the agenda.',
    true,
    'MANAGER_ONLY',
    TIMESTAMP '2026-08-27 15:00:00',
    TIMESTAMP '2026-08-27 15:00:00'
  UNION ALL
  SELECT
    'seed-feedback-0003',
    'chris-davis',
    'project-abc',
    'Jordan Lee',
    'jordan.lee@example.com',
    TIMESTAMP '2026-09-04 15:00:00',
    'RECOGNITION',
    'COLLABORATION',
    'Chris paired with the customer analytics team to rebuild the daily revenue notebook they had been maintaining by hand.',
    'The customer team now refreshes that notebook from the shared job, and the manual spreadsheet handoff stopped.',
    CAST(NULL AS STRING),
    false,
    'MANAGER_ONLY',
    TIMESTAMP '2026-09-04 15:00:00',
    TIMESTAMP '2026-09-04 15:00:00'
) AS source
ON target.feedback_id = source.feedback_id
WHEN NOT MATCHED THEN INSERT *;
