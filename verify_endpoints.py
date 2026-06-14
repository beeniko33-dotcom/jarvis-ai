import json
import urllib.request

results = {}

for path in ['/', '/command', '/test']:
    url = 'http://127.0.0.1:8002' + path
    try:
        if path == '/command':
            data = json.dumps({'command': 'hello world'}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            results[path] = {
                'status': resp.getcode(),
                'body': resp.read().decode('utf-8', errors='replace')
            }
    except Exception as e:
        results[path] = {'error': str(e)}

with open('verify_endpoints_result.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
print('verification complete')
