import json, traceback
result = {}
try:
    from fastapi.testclient import TestClient
    from api import bridge
    client = TestClient(bridge.app)
    r = client.get('/')
    result['root'] = {'status_code': r.status_code, 'json': r.json()}
    r2 = client.post('/command', json={'command': 'hello world'})
    result['command'] = {'status_code': r2.status_code, 'json': r2.json()}
except Exception:
    result['error'] = traceback.format_exc()
with open('run_bridge_test_result.json','w') as f:
    json.dump(result, f, indent=2)
print('wrote run_bridge_test_result.json')
