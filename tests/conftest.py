import pytest
from my_paldea import create_app, db
from my_paldea.paldea_app.models import User, Category


@pytest.fixture
def app():
    """
    Create a fresh Flask application and database for testing.
    Uses your actual create_app() factory.
    """
    app = create_app()

    # Test-specific configuration
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,   # disable CSRF for easier form POST testing
        LOGIN_DISABLED=False,
    )

    with app.app_context():
        # Reset the database
        db.drop_all()
        db.create_all()

        # Create real admin user used by the application
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password="admin123",   # <<<< correct password
        )
        db.session.add(admin_user)

        # Add two categories (used in transactions and budget forms)
        groceries = Category(name="Groceries")
        rent = Category(name="Rent")
        db.session.add_all([groceries, rent])

        db.session.commit()

        yield app

        # Cleanup
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Return Flask test client."""
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    """
    Logs in using admin / admin123
    and returns an authenticated test client.
    """
    client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )
    return client
