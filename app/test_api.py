from fastapi.testclient import TestClient
from main import app, MEMORY_DB

client = TestClient(app)


def setup_function():
    MEMORY_DB.clear()


def test_request_otp():
    response = client.post(
        "/otprequest",
        json={"email": "user@test.com"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "user@test.com" in MEMORY_DB


def test_request_otp_twice():
    client.post(
        "/otprequest",
        json={"email": "user@test.com"}
    )

    response = client.post(
        "/otprequest",
        json={"email": "user@test.com"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "error"


def test_validate_correct_otp():
    client.post(
        "/otprequest",
        json={"email": "user@test.com"}
    )

    otp = MEMORY_DB["user@test.com"]["otp"]

    response = client.post(
        "/otpvalidate",
        json={
            "email": "user@test.com",
            "otp": otp
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "user@test.com" not in MEMORY_DB


def test_validate_wrong_otp():
    client.post(
        "/otprequest",
        json={"email": "user@test.com"}
    )

    response = client.post(
        "/otpvalidate",
        json={
            "email": "user@test.com",
            "otp": "000000"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "error"


def test_get_all_otps():
    client.post(
        "/otprequest",
        json={"email": "user@test.com"}
    )

    response = client.get("/allotps/")

    assert response.status_code == 200
    assert "user@test.com" in response.json()