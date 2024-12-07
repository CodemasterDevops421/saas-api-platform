-- Partition api_requests table by date
CREATE TABLE api_requests_partitioned (
    LIKE api_requests INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- Create partitions for each month
CREATE TABLE api_requests_y2024m01 
    PARTITION OF api_requests_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE api_requests_y2024m02 
    PARTITION OF api_requests_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Create indexes on partitioned table
CREATE INDEX idx_api_requests_part_user_date ON api_requests_partitioned (user_id, created_at);

-- Function to create future partitions
CREATE OR REPLACE FUNCTION create_api_requests_partition()
RETURNS void AS $$
DECLARE
    next_month date;
BEGIN
    next_month := date_trunc('month', now()) + interval '1 month';
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS api_requests_y%sm%s 
         PARTITION OF api_requests_partitioned
         FOR VALUES FROM (%L) TO (%L)',
        to_char(next_month, 'YYYY'),
        to_char(next_month, 'MM'),
        next_month,
        next_month + interval '1 month'
    );
END;
$$ LANGUAGE plpgsql;