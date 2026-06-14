import urllib.request

url = 'http://127.0.0.1:8000/'
try:
    with urllib.request.urlopen(url, timeout=5) as resp:
        print('STATUS', resp.status)
        print(resp.read().decode('utf-8'))
except Exception as e:
    print('ERROR', repr(e))
