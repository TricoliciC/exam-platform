"""Testeaza parse_txt pe Drept penal.txt."""
import os
import io
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_parser import parse_txt

f = "user_uploads/Drept penal.txt"
if not os.path.exists(f):
    print(f"Nu gasesc: {f}")
    sys.exit(1)

questions = parse_txt(f)
print(f"Intrebari extrase: {len(questions)}")

if questions:
    print(f"\nPrima intrebare:")
    q = questions[0]
    print(f"  Text: {q['question'][:80]}")
    print(f"  Optiuni: {list(q['options'].keys())}")
    for k, v in q['options'].items():
        print(f"    {k}) {v[:60]}")
    print(f"  Correct: {q['correct_answer']}")

    print(f"\nUltima intrebare:")
    q = questions[-1]
    print(f"  Text: {q['question'][:80]}")
    print(f"  Correct: {q['correct_answer']}")

# Statistici
print()
print("Statistici:")
print(f"  Cu 4 optiuni: {sum(1 for q in questions if len(q['options']) == 4)}")
print(f"  Cu 3 optiuni: {sum(1 for q in questions if len(q['options']) == 3)}")
print(f"  Cu alte nr: {sum(1 for q in questions if len(q['options']) not in (3, 4))}")
print(f"  Raspunsuri 'a': {sum(1 for q in questions if q['correct_answer'] == 'a')}")
print(f"  Raspunsuri 'b': {sum(1 for q in questions if q['correct_answer'] == 'b')}")
print(f"  Raspunsuri 'c': {sum(1 for q in questions if q['correct_answer'] == 'c')}")
print(f"  Raspunsuri 'd': {sum(1 for q in questions if q['correct_answer'] == 'd')}")
print(f"  Cu placeholder '[nespecificat]': {sum(1 for q in questions if '[nespecificat]' in q['options'].get('d', ''))}")
