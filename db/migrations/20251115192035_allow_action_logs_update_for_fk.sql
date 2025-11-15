-- migrate:up

-- Drop the old trigger first, then the function
DROP TRIGGER IF EXISTS block_action_logs_update ON action_logs;
DROP TRIGGER IF EXISTS block_action_logs_delete ON action_logs;
DROP FUNCTION IF EXISTS prevent_action_logs_modification();

-- Create new function that only prevents DELETE, allows UPDATE
CREATE OR REPLACE FUNCTION prevent_action_logs_deletion()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Deletion of action_logs is not allowed';
END;
$$ LANGUAGE plpgsql;

-- Keep the DELETE trigger
CREATE TRIGGER block_action_logs_delete
  BEFORE DELETE ON action_logs
  FOR EACH ROW
  EXECUTE FUNCTION prevent_action_logs_deletion();

-- migrate:down

-- Restore original behavior
DROP TRIGGER IF EXISTS block_action_logs_delete ON action_logs;
DROP FUNCTION IF EXISTS prevent_action_logs_deletion();

CREATE OR REPLACE FUNCTION prevent_action_logs_modification()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Modification of action_logs is not allowed';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER block_action_logs_update
  BEFORE UPDATE ON action_logs
  FOR EACH ROW
  EXECUTE FUNCTION prevent_action_logs_modification();

CREATE TRIGGER block_action_logs_delete
  BEFORE DELETE ON action_logs
  FOR EACH ROW
  EXECUTE FUNCTION prevent_action_logs_modification();
