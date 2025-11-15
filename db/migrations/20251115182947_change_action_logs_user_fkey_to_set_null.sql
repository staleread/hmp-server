-- migrate:up

-- Update action_logs table: Change user_id foreign key from RESTRICT to SET NULL
ALTER TABLE action_logs
  DROP CONSTRAINT action_logs_user_id_fkey,
  ADD CONSTRAINT action_logs_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

-- migrate:down

-- Revert action_logs table: Change user_id foreign key back to RESTRICT
ALTER TABLE action_logs
  DROP CONSTRAINT action_logs_user_id_fkey,
  ADD CONSTRAINT action_logs_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;

