"""Test real de upload: simuleaza exact ce face frontend-ul."""
import os
import io
import sys
import json
import urllib.request
import urllib.error
import urllib.parse

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 1. Login
print("1) Login admin...")
login_data = json.dumps({"email": "admin@example.com", "password": "admin123"}).encode()
req = urllib.request.Request(
    "http://localhost:5000/api/auth/login",
    data=login_data,
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read())
        token = body["access_token"]
        print(f"   OK, token obtinut")
except urllib.error.HTTPError as e:
    print(f"   EROARE LOGIN: {e.code} {e.read().decode()}")
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"   EROARE CONEXIUNE: {e}")
    print("   Backend-ul ruleaza pe localhost:5000?")
    sys.exit(1)

# 2. Get categories
print("\n2) Get categories...")
try:
    req = urllib.request.Request("http://localhost:5000/api/exams/categories")
    with urllib.request.urlopen(req) as resp:
        cats = json.loads(resp.read())["categories"]
        print(f"   Categorii disponibile: {len(cats)}")
        for c in cats:
            print(f"     - id={c['id']} name={c['name']}")
        if not cats:
            print("   EROARE: nu exista categorii!")
            sys.exit(1)
        category_id = cats[0]["id"]
except Exception as e:
    print(f"   EROARE: {e}")
    sys.exit(1)

# 3. Upload TXT
print("\n3) Upload Drept penal.txt...")
txt_path = "user_uploads/Drept penal.txt"
if not os.path.exists(txt_path):
    print(f"   Nu gasesc: {txt_path}")
    sys.exit(1)

with open(txt_path, "rb") as f:
    txt_bytes = f.read()

boundary = "----FormBoundary" + os.urandom(8).hex()
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="title"\r\n\r\n'
    f"Test Drept Penal\r\n"
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="description"\r\n\r\n'
    f"Examen test drept penal\r\n"
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="category_id"\r\n\r\n'
    f"{category_id}\r\n"
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="txt_file"; filename="Drept penal.txt"\r\n'
    f"Content-Type: text/plain\r\n\r\n"
).encode() + txt_bytes + f"\r\n--{boundary}--\r\n".encode()

req = urllib.request.Request(
    "http://localhost:5000/api/admin/exams",
    data=body,
    headers={
        "Authorization": "Bearer " + token,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    },
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print("   OK! Examen creat:")
        print(f"   ID: {result['exam']['id']}")
        print(f"   Titlu: {result['exam']['title']}")
        print(f"   Intrebari: {result['questions_count']}")
except urllib.error.HTTPError as e:
    print(f"   EROARE HTTP {e.code}:")
    print(f"   Body: {e.read().decode()}")
    sys.exit(1)
except Exception as e:
    print(f"   EROARE: {e}")
    sys.exit(1)
