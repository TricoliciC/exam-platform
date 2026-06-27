"""Test complet: login -> start attempt -> submit WRONG answers -> check result."""
import os, sys, io, json, urllib.request, urllib.error

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE = "http://localhost:5000"

def api(method, path, data=None, token=None):
    url = BASE + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  EROARE {e.code}: {e.read().decode()}")
        return None

# 1. Login
print("1) Login...")
r = api("POST", "/api/auth/login", {"email": "admin@example.com", "password": "admin123"})
if not r:
    sys.exit(1)
token = r["access_token"]
print(f"   Token OK")

# 2. Get exams
print("\n2) Exams...")
r = api("GET", "/api/exams/exams")
if not r or not r.get("exams"):
    print("   Nu exista examene!")
    sys.exit(1)
exam = r["exams"][0]
exam_id = exam["id"]
print(f"   Examen: '{exam['title']}' (ID={exam_id}) cu {exam['question_count']} intrebari")

# 3. Get full exam with questions
print(f"\n3) Exam detail...")
r = api("GET", f"/api/exams/exams/{exam_id}")
if not r:
    sys.exit(1)
questions = r["questions"]
print(f"   {len(questions)} intrebari")

# Show first 3 questions with their correct answers
for q in questions[:3]:
    print(f"   Q{q['order']} (id={q['id']}): {q['question_text'][:60]}...")
    print(f"      a) {q['option_a'][:40]}")
    print(f"      b) {q['option_b'][:40]}")
    print(f"      c) {q['option_c'][:40]}")
    print(f"      d) {q['option_d'][:40]}")
    print(f"      CORECT: {q['correct_answer']}")

# 4. Start attempt
print(f"\n4) Start attempt...")
r = api("POST", "/api/exams/attempts/start", {"exam_id": exam_id}, token)
if not r:
    sys.exit(1)
attempt_id = r["attempt_id"]
print(f"   Attempt ID={attempt_id}")

# 5. Submit DELIBERATELY WRONG answers for first 5 questions
print(f"\n5) Submit with WRONG answers...")
wrong_answers = []
for q in questions[:5]:
    correct = q["correct_answer"]
    # Pick a DIFFERENT letter
    wrong = {"a": "b", "b": "c", "c": "a"}.get(correct, "b")
    wrong_answers.append({"question_id": q["id"], "selected_answer": wrong})
    print(f"   Q{q['order']} (id={q['id']}): corect={correct}, trimit={wrong}")

r = api("POST", f"/api/exams/attempts/{attempt_id}/submit", {"answers": wrong_answers}, token)
if not r:
    sys.exit(1)
attempt = r["attempt"]
print(f"\n   Rezultat: score={attempt['score']}%, correct={attempt['correct_answers']}/{attempt['total_questions']}")
print(f"   EXPECTED: score=0% (toate gresite)")

if attempt["score"] == 100:
    print("\n*** BUG CONFIRMAT: Totul e marcat corect! ***")
elif attempt["score"] == 0:
    print("\n*** Totul e corect (scor 0 pentru raspunsuri gresite) ***")
else:
    print(f"\n*** Scor partial: {attempt['score']}% ***")

# 6. Get attempt details
print(f"\n6) Detalii attempt...")
r = api("GET", f"/api/exams/attempts/{attempt_id}", None, token)
if r:
    print(f"   Score din DB: {r['attempt']['score']}%")
    for ans in r.get("answers", []):
        q = ans.get("question", {})
        print(f"   Q{q.get('id')}: ales={ans['selected_answer']}, corect={q.get('correct_answer')}, is_correct={ans['is_correct']}")
