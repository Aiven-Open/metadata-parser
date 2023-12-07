import pytest

# Assuming the Dash app is initialized in a file named app.py and the server is an attribute of the app
from app import app


@pytest.fixture(scope='module')
def client():
    return app.server.test_client()

def test_server_is_up_and_running(client):
    response = client.head('http://127.0.0.1:8050/')
    assert response.status_code == 200

