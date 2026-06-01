"""Push git commits and tags to remote via PowerShell (bypasses WSL network)."""
import subprocess
import sys

repo_dir = r'D:\Desktop\hermes\ai-company-wars\teams\red\project'

token = subprocess.check_output(
    ['powershell.exe', '-Command',
     '[Environment]::GetEnvironmentVariable(\'GITHUB_TOKEN_Classic\', \'User\')'],
    text=True
).strip()

cmd = f'''
$ErrorActionPreference = "Stop"
cd "{repo_dir}"
Write-Output "=== Setting remote URL ==="
git remote set-url origin https://oauth2:{token}@github.com/0717lq/ai-company-wars-red.git
Write-Output "=== Pushing main + tags ==="
git push origin main --tags 2>&1
if ($LASTEXITCODE -ne 0) {{ throw "git push failed with exit code $LASTEXITCODE" }}
Write-Output "=== Restoring remote URL ==="
git remote set-url origin https://github.com/0717lq/ai-company-wars-red.git
Write-Output "=== DONE ==="
'''

result = subprocess.run(
    ['powershell.exe', '-Command', cmd],
    capture_output=True, timeout=90
)
# Decode with errors='replace' to handle encoding issues
stdout = result.stdout.decode('utf-8', errors='replace')
stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''

print("STDOUT:", stdout)
if stderr:
    print("STDERR:", stderr)
if result.returncode != 0:
    print(f"EXIT CODE: {result.returncode}")
    sys.exit(result.returncode)
