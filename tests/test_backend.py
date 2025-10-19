import os
import json
import pytest

# Ensure tests use the mock assistant provider to avoid external API calls
os.environ.setdefault('ASSISTANT_PROVIDER', 'mock')

from backend import app as backend_app


@pytest.fixture
def client():
    backend_app.app.config['TESTING'] = True
    with backend_app.app.test_client() as client:
        yield client


def test_ping(client):
    rv = client.get('/ping')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'ok'


def test_assist_echo(client):
    rv = client.post('/assist', json={'message': 'hello'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert '(mock) I understood: hello' in data.get('reply', '')


def test_assist_no_message(client):
    rv = client.post('/assist', json={})
    assert rv.status_code == 400
    data = rv.get_json()
    assert 'error' in data
