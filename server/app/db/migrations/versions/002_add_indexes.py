from alembic import op

def upgrade():
    # Add indexes for frequently accessed columns
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_status', 'users', ['status'])
    op.create_index('idx_api_requests_created', 'api_requests', ['created_at'])
    op.create_index('idx_api_requests_user', 'api_requests', ['user_id'])
    op.create_index('idx_subscriptions_status', 'subscriptions', ['status'])
    
    # Add composite indexes
    op.create_index(
        'idx_api_requests_user_date',
        'api_requests',
        ['user_id', 'created_at']
    )

def downgrade():
    op.drop_index('idx_user_email')
    op.drop_index('idx_user_status')
    op.drop_index('idx_api_requests_created')
    op.drop_index('idx_api_requests_user')
    op.drop_index('idx_subscriptions_status')
    op.drop_index('idx_api_requests_user_date')