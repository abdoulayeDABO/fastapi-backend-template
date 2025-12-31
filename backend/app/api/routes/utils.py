from fastapi import APIRouter, BackgroundTasks
from pydantic.networks import EmailStr

from app.models.users import Message
from app.utils.email import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    # dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.post(
    "/test-background-email/",
    status_code=201,
)
async def test_background_email(
    email_to: EmailStr, background_tasks: BackgroundTasks
) -> Message:
    """
    Test background emails.
    """
    email_data = generate_test_email(email_to=email_to)
    background_tasks.add_task(
        send_email,
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Notification sent in the background")


@router.get(
    "/health-check/",
    status_code=200,
)
def check_health() -> Message:
    return Message(message="Ok")
