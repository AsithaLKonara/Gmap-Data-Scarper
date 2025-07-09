-- Add indexes for performance optimization
ALTER TABLE jobs ADD INDEX idx_jobs_user_id (user_id);
ALTER TABLE jobs ADD INDEX idx_jobs_status (status);
ALTER TABLE leads ADD INDEX idx_leads_user_id (user_id);
ALTER TABLE leads ADD INDEX idx_leads_status (status);
ALTER TABLE audit_logs ADD INDEX idx_audit_logs_user_id (user_id);
ALTER TABLE notifications ADD INDEX idx_notifications_user_id (user_id);
ALTER TABLE scheduled_jobs ADD INDEX idx_scheduled_jobs_user_id (user_id);
ALTER TABLE custom_dashboards ADD INDEX idx_custom_dashboards_user_id (user_id);
ALTER TABLE teams ADD INDEX idx_teams_owner_id (owner_id);
ALTER TABLE team_memberships ADD INDEX idx_team_memberships_team_id (team_id);
ALTER TABLE team_memberships ADD INDEX idx_team_memberships_user_id (user_id); 