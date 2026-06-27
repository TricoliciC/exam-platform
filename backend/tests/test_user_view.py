"""Testeaza ce vede un user normal pe site (fara login)."""
import os
import io
import sys
import json
import urllib.request

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

print("=== CA USER NORMAL (fara login) ===\n")

# 1. Toate examenele
print("1) GET /api/exams (toate)")
req = urllib.request.Request("http://localhost:5000/api/exams")
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
    print(f"   Total examene: {len(data['exams'])}")
    for e in data['exams']:
        print(f"   - ID={e['id']} '{e['title']}' | category='{e['category_name']}' | active={e['is_active']} | q={e['question_count']}")

print()

# 2. Filtrat pe categoria Drept (id=4)
print("2) GET /api/exams?category_id=4 (Drept)")
req = urllib.request.Request("http://localhost:5000/api/exams?category_id=4")
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
    print(f"   Examene in Drept: {len(data['exams'])}")
    for e in data['exams']:
        print(f"   - ID={e['id']} '{e['title']}' | q={e['question_count']}")

print()

# 3. Categorii
print("3) GET /api/exams/categories")
req = urllib.request.Request("http://localhost:5000/api/exams/categories")
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
    print(f"   Categorii: {len(data['categories'])}")
    for c in data['categories']:
        print(f"   - ID={c['id']} '{c['name']}'")
