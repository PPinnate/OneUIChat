from fastapi.testclient import TestClient

from app.main import app, download_manager


client = TestClient(app)


def test_get_models_ok():
    response = client.get('/models')
    assert response.status_code == 200
    payload = response.json()
    assert 'models' in payload


def test_set_token_validation():
    response = client.post('/settings/token', json={'token': 'short'})
    assert response.status_code == 422


def test_model_explore_ok(monkeypatch):
    monkeypatch.setattr(
        download_manager,
        'probe_repo',
        lambda repo_id, token=None: {
            'available': True,
            'auth_required': False,
            'error': None,
            'total_bytes': 1024,
            'total_gb': 0.0,
            'files': [{'path': 'model.gguf', 'size': 1024}],
        },
    )
    response = client.post('/models/explore', json={'model_id': 'chat.qwen3-next-80b-a3b', 'variant_id': 'Q2_K'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['probe']['available'] is True
    assert 'ready_to_download' in payload
