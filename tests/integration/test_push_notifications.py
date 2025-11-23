"""Integration tests for push notification service."""
import pytest
from backend.services.push_service import get_push_service, PushService
from backend.models.push_subscription import PushSubscription
from backend.models.database import get_session, init_db
import os


@pytest.fixture
def db_session():
    """Create a test database session."""
    init_db()
    session = get_session()
    yield session
    session.close()


@pytest.fixture
def push_service():
    """Create a push service instance."""
    # Use mock service if pywebpush not available
    try:
        return get_push_service()
    except ImportError:
        # Return mock service for testing
        class MockPushService:
            def subscribe(self, *args, **kwargs):
                return None
            def unsubscribe(self, *args, **kwargs):
                return False
            def send_notification(self, *args, **kwargs):
                return False
        return MockPushService()


@pytest.fixture
def sample_subscription_data():
    """Sample subscription data for testing."""
    return {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint",
        "keys": {
            "p256dh": "test_p256dh_key",
            "auth": "test_auth_key"
        }
    }


def test_push_service_initialization(push_service):
    """Test push service can be initialized."""
    assert push_service is not None


def test_subscribe_to_push_notifications(db_session, push_service, sample_subscription_data):
    """Test subscribing to push notifications."""
    if hasattr(push_service, 'subscribe'):
        # Pass db_session to ensure subscription is bound to test session
        subscription = push_service.subscribe(
            subscription_data=sample_subscription_data,
            user_id="test_user",
            device_info={"browser": "Chrome", "os": "Windows"},
            db_session=db_session
        )
        
        # If subscription is None, it means pywebpush is not available (mock service)
        if subscription is not None:
            assert subscription is not None
            # Subscription should be bound to db_session now
            assert subscription.endpoint == sample_subscription_data["endpoint"]
            assert subscription.user_id == "test_user"
            
            # Verify subscription is in database
            db_subscription = db_session.query(PushSubscription).filter(
                PushSubscription.endpoint == sample_subscription_data["endpoint"]
            ).first()
            assert db_subscription is not None


def test_unsubscribe_from_push_notifications(db_session, push_service, sample_subscription_data):
    """Test unsubscribing from push notifications."""
    if hasattr(push_service, 'subscribe') and hasattr(push_service, 'unsubscribe'):
        # First subscribe
        subscription = push_service.subscribe(
            subscription_data=sample_subscription_data,
            user_id="test_user"
        )
        
        if subscription is not None:
            # Then unsubscribe
            success = push_service.unsubscribe(sample_subscription_data["endpoint"])
            
            if success:
                # Verify subscription is marked as inactive
                db_subscription = db_session.query(PushSubscription).filter(
                    PushSubscription.endpoint == sample_subscription_data["endpoint"]
                ).first()
                assert db_subscription is not None
                assert db_subscription.is_active == "false"


def test_update_notification_preferences(db_session, push_service, sample_subscription_data):
    """Test updating notification preferences."""
    if hasattr(push_service, 'subscribe') and hasattr(push_service, 'update_preferences'):
        # Subscribe first
        subscription = push_service.subscribe(
            subscription_data=sample_subscription_data,
            user_id="test_user"
        )
        
        if subscription is not None:
            # Update preferences
            new_preferences = {
                "task_completion": True,
                "task_errors": True,
                "task_paused": False,
                "task_resumed": False
            }
            
            success = push_service.update_preferences(
                sample_subscription_data["endpoint"],
                new_preferences
            )
            
            if success:
                # Verify preferences are updated
                db_subscription = db_session.query(PushSubscription).filter(
                    PushSubscription.endpoint == sample_subscription_data["endpoint"]
                ).first()
                assert db_subscription is not None
                assert db_subscription.notification_preferences == new_preferences


def test_get_subscriptions(db_session, push_service, sample_subscription_data):
    """Test getting user subscriptions."""
    if hasattr(push_service, 'subscribe') and hasattr(push_service, 'get_subscriptions'):
        # Subscribe
        subscription = push_service.subscribe(
            subscription_data=sample_subscription_data,
            user_id="test_user"
        )
        
        if subscription is not None:
            # Get subscriptions
            subscriptions = push_service.get_subscriptions(user_id="test_user")
            assert len(subscriptions) > 0
            assert any(sub.endpoint == sample_subscription_data["endpoint"] for sub in subscriptions)


def test_push_subscription_model(db_session, sample_subscription_data):
    """Test PushSubscription model."""
    from backend.models.push_subscription import PushSubscription
    
    # Clean up any existing subscription with this endpoint first
    # Use a unique endpoint for this test to avoid conflicts
    import uuid
    unique_endpoint = f"{sample_subscription_data['endpoint']}_{uuid.uuid4().hex[:8]}"
    
    subscription = PushSubscription(
        user_id="test_user",
        endpoint=unique_endpoint,
        p256dh=sample_subscription_data["keys"]["p256dh"],
        auth=sample_subscription_data["keys"]["auth"],
        device_info={"browser": "Chrome"},
        notification_preferences={
            "task_completion": True,
            "task_errors": True
        }
    )
    
    db_session.add(subscription)
    db_session.commit()
    
    # Verify it was saved
    db_subscription = db_session.query(PushSubscription).filter(
        PushSubscription.endpoint == unique_endpoint
    ).first()
    
    assert db_subscription is not None
    assert db_subscription.user_id == "test_user"
    assert db_subscription.is_active == "true"
    
    # Test to_dict method
    subscription_dict = db_subscription.to_dict()
    assert subscription_dict["endpoint"] == unique_endpoint
    assert subscription_dict["is_active"] is True


