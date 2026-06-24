import os
import requests

raw_url = os.environ.get('CLOUDFLARE_WORKER_URL', '')
key = os.environ.get('DASHBOARD_API_KEY', '')

print('RAW URL from secret:', raw_url)
print('Key length:', len(key))
print('Key value:', key)  # print full key since it's temporary debug

# Try the URL as-is first
url1 = raw_url.rstrip('/')
print('\n--- Test 1: URL as-is ---')
print('URL:', url1 + '/api/kv?key=test')
try:
    r = requests.get(url1 + '/api/kv?key=test', headers={'X-Dashboard-Key': key}, timeout=10)
    print('Status:', r.status_code)
    print('Response:', r.text[:200])
except Exception as e:
    print('Error:', e)

# Try stripping /generate
url2 = raw_url.rstrip('/').replace('/generate', '')
print('\n--- Test 2: URL with /generate stripped ---')
print('URL:', url2 + '/api/kv?key=test')
try:
    r = requests.get(url2 + '/api/kv?key=test', headers={'X-Dashboard-Key': key}, timeout=10)
    print('Status:', r.status_code)
    print('Response:', r.text[:200])
except Exception as e:
    print('Error:', e)
