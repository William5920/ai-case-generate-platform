import glob
import os

files = glob.glob(r'd:\workspace\ai-case-generate-platform\backend\app\routers\*_router.py')
old = 'current_user["id"]'
new = 'current_user.id'

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    if old in content:
        content = content.replace(old, new)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f"Updated: {f}")
    else:
        print(f"No change: {f}")
