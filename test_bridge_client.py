from fastapi.testclient import TestClient
from api import bridge

client = TestClient(bridge.app)

r = client.get('/')
print('GET / ->', r.status_code, r.json())

r2 = client.post('/command', json={'command': 'hello world'})
print('POST /command ->', r2.status_code, r2.json())
