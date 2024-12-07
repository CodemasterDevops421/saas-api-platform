#!/bin/bash

# Clean up test data
echo "Cleaning up test data..."

# Reset Redis cache
redis-cli FLUSHALL

# Reset test database
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "
DELETE FROM api_requests WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@test.com');
DELETE FROM subscriptions WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@test.com');
DELETE FROM users WHERE email LIKE '%@test.com';"

# Clear test logs
find /var/log/saas-platform -name "*.log" -mtime +1 -delete

# Reset monitoring data
curl -X POST http://localhost:9090/-/reload

echo "Cleanup complete"