#!/bin/bash

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
S3_BUCKET="s3://saas-platform-backups"

# Create backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME -F c -f "$BACKUP_DIR/db_$TIMESTAMP.dump"

# Compress backup
gzip "$BACKUP_DIR/db_$TIMESTAMP.dump"

# Upload to S3
aws s3 cp "$BACKUP_DIR/db_$TIMESTAMP.dump.gz" "$S3_BUCKET/db/db_$TIMESTAMP.dump.gz"

# Keep only last 7 days of local backups
find $BACKUP_DIR -type f -mtime +7 -delete

# Notify monitoring
curl -X POST $MONITORING_WEBHOOK -H "Content-Type: application/json" \
  -d "{\"event\": \"backup_completed\", \"timestamp\": \"$TIMESTAMP\"}"