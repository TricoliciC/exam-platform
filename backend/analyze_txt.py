"""Analizeaza un fisier .txt din user_uploads si raporteaza probleme."""
import os
import io
import sys
import re

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

UPLOAD_DIR = "user_uploads"

# Cauta fisierul
target = None
for f in os.listdir(UPLOAD_DIR):
    if "drept" in f.lower() and f.lower().endswith(".txt"):
        target = os.path.join(UPLOAD_DIR, f)
        break

if not target:
    print("Nu am gasit niciun fisier Drept penal.txt")
    print("Fisiere disponibile:")
    for f in os.listdir(UPLOAD_DIR):
        print(f"  - {f}")
    sys.exit(1)

print(f"Fisier: {target}")
print(f"Size: {os.path.getsize(target)} bytes")

# Citeste cu detectie encoding
text = None
for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
    try:
        with open(target, "r", encoding=enc) as fp:
            text = fp.read()
        print(f"Encoding: {enc} OK")
        break
    except UnicodeDecodeError as e:
        print(f"  {enc} failed: {e}")

if text is None:
    print("EROARE: nu pot citi fisierul in niciun encoding")
    sys.exit(1)

lines = text.split("\n")
print(f"Total linii: {len(lines)}")
print(f"Linii non-empty: {sum(1 for l in lines if l.strip())}")
print()

# Verifica BOM
bom = text[:3]
if bom == "\ufeff" or text.startswith("\ufeff"):
    print("ATENTIE: Fisierul are BOM (Byte Order Mark) la inceput")
    print("   -> poate cauza probleme la parsare")
    print()

# Verifica terminator de linie
crlf = text.count("\r\n")
lf = text.count("\n") - crlf
print(f"Terminatori linie: CRLF={crlf}, LF={lf}")
if crlf > 0 and lf > 0:
    print("ATENTIE: mix de CRLF si LF - poate cauza probleme")
    print()

# Cauta intrebari (regex)
question_re = re.compile(r"^\d+[\.\)]\s*(.+)$", re.MULTILINE)
questions = question_re.findall(text)
print(f"Intrebari detectate (regex 'N. text'): {len(questions)}")

# Cauta optiuni
option_re = re.compile(r"^([a-d])\s*[\)\.]\s*(.+)$", re.MULTILINE | re.IGNORECASE)
options = option_re.findall(text)
print(f"Optiuni detectate (regex 'a) text'): {len(options)}")

# Cauta Correct markers
correct_re = re.compile(r"^\s*(?:correct|corect|raspuns|answer)\s*[:\-=]?\s*([a-d])\b", re.MULTILINE | re.IGNORECASE)
corrects = correct_re.findall(text)
print(f"Markeri 'Correct: x' detectati: {len(corrects)}")

# Cauta '?' markers (need manual completion)
need_manual = re.findall(r"Correct:\s*\?", text, re.IGNORECASE)
print(f"Intrebari cu 'Correct: ?' (necesita completare): {len(need_manual)}")

print()
print("=== PRIMELE 25 LINII ===")
for i, line in enumerate(lines[:25]):
    print(f"{i+1:3}: {repr(line)}")

print()
print("=== ULTIMELE 10 LINII ===")
for i, line in enumerate(lines[-10:], start=len(lines)-9):
    print(f"{i:3}: {repr(line)}")

print()
print("=== ANALIZA STRUCTURII ===")

# Grupeaza optiunile pe intrebare
# Gaseste pozitiile intrebarilor
question_positions = [(m.start(), m.group(0)) for m in question_re.finditer(text)]
print(f"Pozitii intrebari gasite: {len(question_positions)}")

if question_positions:
    # Verifica daca toate intrebarile au macar 3 optiuni
    problems = []
    for idx, (pos, qtext) in enumerate(question_positions):
        # Determina sfarsitul block-ului (urmatoarea intrebare sau EOF)
        if idx + 1 < len(question_positions):
            end_pos = question_positions[idx + 1][0]
        else:
            end_pos = len(text)
        block = text[pos:end_pos]
        opts = option_re.findall(block)
        opt_letters = [o[0].lower() for o in opts]
        has_correct = bool(correct_re.search(block))
        is_question_mark = "?" in qtext
        needs_3plus = len(opt_letters) < 3
        if needs_3plus or not is_question_mark:
            problems.append({
                "idx": idx + 1,
                "text": qtext[:60],
                "options": opt_letters,
                "has_correct": has_correct,
                "is_question": is_question_mark,
            })

    if problems:
        print(f"\nProbleme detectate in {len(problems)} intrebari:")
        for p in problems[:20]:
            reasons = []
            if not p["is_question"]:
                reasons.append("nu pare intrebare (fara '?')")
            if len(p["options"]) < 3:
                reasons.append(f"doar {len(p['options'])} optiuni")
            if not p["has_correct"]:
                reasons.append("fara 'Correct: x'")
            print(f"  - #{p['idx']}: '{p['text']}' | optiuni={p['options']} | {', '.join(reasons)}")
        if len(problems) > 20:
            print(f"  ... si inca {len(problems) - 20} probleme")

    # Statistici
    with_correct = sum(1 for idx, (pos, _) in enumerate(question_positions)
                       if (lambda: bool(correct_re.search(text[pos:question_positions[idx+1][0] if idx+1 < len(question_positions) else len(text)])))())
    print(f"\nIntrebari cu 'Correct: x' valid: {with_correct}")

# Verifica daca exista linii cu caractere ciudate
weird_chars = set()
for line in lines:
    for ch in line:
        if ord(ch) > 127 and ch not in "ăâîșțĂÂÎȘȚ":
            weird_chars.add(ch)
if weird_chars:
    print(f"\nATENTIE: caractere non-ASCII neobisnuite: {weird_chars}")
