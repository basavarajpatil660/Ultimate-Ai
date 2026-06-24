import os
import requests

url = os.environ.get('CLOUDFLARE_WORKER_URL', '').rstrip('/').replace('/generate', '')
key = os.environ.get('DASHBOARD_API_KEY', '')

print('Worker URL:', url)
print('Key length:', len(key))
print('Key first 4 chars:', key[:4])

r = requests.get(url + '/api/kv?key=test', headers={'X-Dashboard-Key': key}, timeout=10)
print('KV test status:', r.status_code)
print('KV response:', r.text[:300])
