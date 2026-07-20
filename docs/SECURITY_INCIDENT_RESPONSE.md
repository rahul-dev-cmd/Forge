# Security Incident Response Plan

## 1. Incident Classification

- **Severity 1 (Critical)**: Compromise of GitHub App private key, DB root credentials, or data breach across workspace boundaries.
- **Severity 2 (High)**: Secret leak in repository logs or unauthorized access attempt.
- **Severity 3 (Medium)**: Denial of service or rate limit abuse.

---

## 2. Emergency Secret Rotation

### GitHub App Private Key Rotation
1. Generate new private key in GitHub App Settings.
2. Update Kubernetes secret `forge-secrets`.
3. Revoke old key in GitHub App settings.
4. Execute `kubectl rollout restart deployment/forge-api`.

### Database Credential Rotation
1. Alter database password in PostgreSQL.
2. Update connection string secret in Kubernetes.
3. Restart API & worker deployments.
