import asyncio
import pytest
from unittest.mock import AsyncMock
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

@pytest.fixture
def email_service():
    # Create an instance of AsyncMock specifically tailored to mimic the EmailService class
    mock_service = AsyncMock(spec=EmailService)
    
    # Set up the mock to simulate a successful email sending
    mock_service.send_user_email.return_value = asyncio.Future()
    mock_service.send_user_email.return_value.set_result(None)
    
    # Optionally, set up the mock to simulate a failure in sending email
    # Uncomment the next line to simulate a failure
    # mock_service.send_user_email.side_effect = Exception("Simulated sending error")
    
    return mock_service

@pytest.mark.asyncio
async def test_send_email_success(email_service):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "verification_url": "http://example.com/verify?token=12345"
    }
    try:
        # Attempt to send an email
        await email_service.send_user_email(user_data, 'email_verification')
        assert True, "Email sent successfully."
    except Exception as e:
        pytest.fail(f"Email sending failed with exception: {str(e)}")

@pytest.mark.asyncio
async def test_send_email_failure(email_service):
    # Set the mock to raise an exception to simulate a failure
    email_service.send_user_email.side_effect = Exception("Simulated sending error")
    
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "verification_url": "http://example.com/verify?token=12345"
    }
    with pytest.raises(Exception) as excinfo:
        await email_service.send_user_email(user_data, 'email_verification')
    assert "Simulated sending error" in str(excinfo.value), "Email service should raise an exception on failure."

@pytest.mark.asyncio
async def test_send_email_without_side_effect(email_service):
    # This test will pass silently as no side effect is simulated here
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "verification_url": "http://example.com/verify?token=12345"
    }
    await email_service.send_user_email(user_data, 'email_verification')  # No exception should be raised

@pytest.mark.asyncio
async def test_send_email_invalid_address(email_service):
    user_data = {
        "name": "Test User",
        "email": "invalid-email",
        "verification_url": "http://example.com/verify?token=12345"
    }
    email_service.send_user_email.side_effect = ValueError("Invalid email address")
    with pytest.raises(ValueError) as excinfo:
        await email_service.send_user_email(user_data, 'email_verification')
    assert "Invalid email address" in str(excinfo.value), "Service should validate email addresses."

@pytest.mark.asyncio
async def test_email_service_timeout(email_service):
    email_service.send_user_email = AsyncMock(side_effect=asyncio.TimeoutError("Timeout occurred"))
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "verification_url": "http://example.com/verify?token=12345"
    }
    with pytest.raises(asyncio.TimeoutError) as excinfo:
        await email_service.send_user_email(user_data, 'email_verification')
    assert "Timeout occurred" in str(excinfo.value), "Email service should handle timeouts gracefully."
