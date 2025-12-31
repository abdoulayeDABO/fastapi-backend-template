from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.security import verify_password
from app.models.users import UserCreate
from app.services.users import create_user
from app.utils.token import generate_password_reset_token
from tests.utils.utils import random_email, random_lower_string


def test_create_user(client: TestClient):
    signup_data = {
        "email": "layedabo@esp.sn",
        "password": "passer1234",
        "full_name": "Abdoualye Dabo",
    }
    response = client.post(f"{settings.API_V1_STR}/signup", json=signup_data)
    assert response.status_code == 201
    assert response.json() == {"message": "Account created successfully"}


def test_register_user_already_exists_error(client: TestClient) -> None:
    password = random_lower_string()
    full_name = random_lower_string()
    data = {
        "email": settings.FIRST_SUPERUSER,
        "password": password,
        "full_name": full_name,
    }
    r = client.post(
        f"{settings.API_V1_STR}/signup",
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "The user with this email already exists in the system"


def test_create_existing_user(client: TestClient, db: Session):
    email = random_email()
    password = random_lower_string()
    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
    )
    create_user(session=db, user_create=user_create)
    response = client.post(
        f"{settings.API_V1_STR}/signup",
        json={
            "email": email,
            "full_name": "Test User",
            "password": password,
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "The user with this email already exists in the system"
    }


def test_send_activation_email(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=False,
        is_superuser=False,
    )
    data = {"email": email}
    create_user(session=db, user_create=user_create)
    response = client.post(f"{settings.API_V1_STR}/activation-email", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "Email sent successfully"}


def test_confirm_signup(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=False,
        is_superuser=False,
    )
    data = {"email": email}
    user = create_user(session=db, user_create=user_create)
    token = generate_password_reset_token(email)
    data = {
        "token": token,
    }

    r = client.post(f"{settings.API_V1_STR}/activate", json=data)

    assert r.json() == {"message": "Account activated successfully"}
    assert r.status_code == 200

    db.refresh(user)
    assert user.is_active is True


def test_confirm_signup_with_bad_token(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=False,
        is_superuser=False,
    )
    data = {"email": email}
    create_user(session=db, user_create=user_create)

    data = {
        "token": "bad token",
    }

    r = client.post(f"{settings.API_V1_STR}/activate", json=data)

    assert r.status_code == 400
    assert r.json() == {"detail": "Invalid token"}


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    r = client.post(f"{settings.API_V1_STR}/access-token", data=login_data)
    assert r.status_code == 400


def test_recovery_password(client: TestClient, db: Session) -> None:
    with (
        patch("app.core.config.settings.SMTP_HOST", "smtp.gmail.com"),
        patch("app.core.config.settings.SMTP_USER", "abdoulayedabo@esp.sn"),
    ):
        email = "test@example.com"
        password = random_lower_string()
        user_create = UserCreate(
            email=email,
            full_name="Test User",
            password=password,
            is_active=True,
            is_superuser=False,
        )
        create_user(session=db, user_create=user_create)
        r = client.post(f"{settings.API_V1_STR}/password-recovery/{email}")
        assert r.status_code == 200
        assert r.json() == {"message": "Password recovery email sent"}


def test_recovery_password_user_not_exits(client: TestClient) -> None:
    email = "jVgQr@example.com"
    r = client.post(f"{settings.API_V1_STR}/password-recovery/{email}")
    assert r.status_code == 404


def test_reset_password(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    new_password = random_lower_string()

    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False,
    )
    user = create_user(session=db, user_create=user_create)
    token = generate_password_reset_token(email=email)

    data = {"new_password": new_password, "token": token}

    r = client.post(
        f"{settings.API_V1_STR}/reset-password",
        json=data,
    )

    assert r.status_code == 200
    assert r.json() == {"message": "Password updated successfully"}

    db.refresh(user)
    assert verify_password(new_password, user.hashed_password)


def test_reset_password_invalid_token(client: TestClient) -> None:
    data = {"new_password": "changethis", "token": "invalid"}
    r = client.post(
        f"{settings.API_V1_STR}/reset-password",
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"
