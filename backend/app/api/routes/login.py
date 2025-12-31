from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel

from app.api.deps import SessionDep
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.users import (
    Message,
    NewPassword,
    Token,
    UserCreate,
    UserRegister,
)
from app.services import users as user_service
from app.utils.email import (
    generate_activation_email,
    generate_confirm_signup_email,
    generate_reset_password_email,
    send_email,
)
from app.utils.token import (
    generate_password_reset_token,
    verify_password_reset_token,
)

router = APIRouter(tags=["auth"])


class ActivateAccount(SQLModel):
    token: str


class SendActivationEmail(SQLModel):
    email: str


@router.post("/signup", status_code=201)
def register_user(
    session: SessionDep, user_in: UserRegister, background_tasks: BackgroundTasks
) -> Any:
    """
    Create new user.
    """
    user = user_service.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = user_service.create_user(session=session, user_create=user_create)
    token = generate_password_reset_token(user_in.email)
    email_data = generate_confirm_signup_email(
        email_to=user_in.email, username=user_in.email, token=token
    )

    background_tasks.add_task(
        send_email,
        email_to=user_in.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Account created successfully")


@router.post("/activation-email", response_model=Message)
def send_activation_email(
    session: SessionDep, body: SendActivationEmail, background_tasks: BackgroundTasks
) -> Any:
    """
    Send activation email
    """
    user = user_service.get_user_by_email(session=session, email=body.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    if user.is_active:
        raise HTTPException(
            status_code=400,
            detail="The user already activated.",
        )
    token = generate_password_reset_token(user.email)
    email_data = generate_activation_email(
        email_to=user.email, username=user.email, token=token
    )
    background_tasks.add_task(
        send_email,
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Email sent successfully")


@router.post("/activate")
def activate(session: SessionDep, body: ActivateAccount) -> Message:
    """
    Activate user account
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = user_service.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    user.is_active = True
    session.add(user)
    session.commit()
    return Message(message="Account activated successfully")


@router.post("/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_service.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Send password Recovery email
    """
    user = user_service.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = user_service.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully")
