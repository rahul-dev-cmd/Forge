# Forge Disaster Recovery & Incident Runbook

## 1. Recovery Objectives (SLA)

- **Recovery Point Objective (RPO)**: $< 1\text{ Hour}$ (Maximum acceptable data loss window)
- **Recovery Time Objective (RTO)**: $< 15\text{ Minutes}$ (Maximum acceptable service downtime window)

---

## 2. PostgreSQL Backup & Restore

### Backup Execution
```bash
pg_dump -h $POSTGRES_HOST -U forge_user -F c -b -v -f forge_backup_$(date +%F).dump forge_db
```

### Disaster Restore
```bash
pg_restore -h $POSTGRES_HOST -U forge_user -d forge_db --clean --if-exists forge_backup.dump
```

---

## 3. Qdrant Vector DB Snapshot Restore

### Take Snapshot
```bash
curl -X POST "http://localhost:6333/collections/forge_vectors/snapshots"
```

### Restore Snapshot
```bash
curl -X POST "http://localhost:6333/collections/forge_vectors/snapshots/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "snapshot=@snapshot-forge_vectors.tar"
```

---

## 4. Worker Queue Recovery

In case of Redis queue stall or background task deadlock:
```bash
# 1. Flush corrupted worker queue key
redis-cli del arq:queue:ai_queue
# 2. Restart worker pods
kubectl rollout restart deployment/forge-worker
```
