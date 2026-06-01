"""创建 GitHub Release via API — 使用 urllib 避免 WSL SSL 问题。"""
import json
import os
import subprocess
import urllib.request
import urllib.error

# 从 Windows 环境读取 token
token = subprocess.check_output(
    ['powershell.exe', '-Command',
     '[Environment]::GetEnvironmentVariable(\'GITHUB_TOKEN_Classic\', \'User\')'],
    text=True
).strip()

if not token:
    print("ERROR: No GitHub token found")
    exit(1)

# 读取 release notes
with open('/mnt/d/Desktop/hermes/ai-company-wars/teams/red/artifacts/release-notes-v0.5.0.md', 'r') as f:
    body = f.read()

payload = {
    'tag_name': 'v0.5.0',
    'target_commitish': 'main',
    'name': 'dirsort v0.5.0 — 代码质量提升',
    'body': body,
    'draft': False,
    'prerelease': False,
    'make_latest': 'true'
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    'https://api.github.com/repos/0717lq/ai-company-wars-red/releases',
    data=data,
    headers={
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
        print(f"✅ Release created: {result['html_url']}")
        print(f"   Tag: {result['tag_name']}")
        print(f"   ID: {result['id']}")
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error {e.code}: {e.read().decode()}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
