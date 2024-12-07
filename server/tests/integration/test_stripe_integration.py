import pytest
from unittest.mock import patch
from app.services.stripe_service import StripeService

@pytest.mark.asyncio
async def test_create_subscription(db_session):
    with patch('stripe.Customer.create') as mock_customer:
        with patch('stripe.Subscription.create') as mock_subscription:
            mock_customer.return_value.id = 'cus_test123'
            mock_subscription.return_value.id = 'sub_test123'
            mock_subscription.return_value.latest_invoice.payment_intent.client_secret = 'secret123'

            result = await StripeService.create_subscription(
                db_session,
                user_id=1,
                price_id='price_test123'
            )

            assert result['subscriptionId'] == 'sub_test123'
            assert result['clientSecret'] == 'secret123'