"""Quick test: parseaza fisierul .txt generat anterior."""
import os
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_parser import parse_txt

txt_file = "user_uploads/TEST pt Examenul de admitere la stagiu primăvara 2026_extracted.txt"

if not os.path.exists(txt_file):
    print(f"Nu gasesc fisierul: {txt_file}")
    print("Fisiere disponibile:")
    for f in os.listdir("user_uploads"):
        print(f"  - {f}")
    sys.exit(1)

print(f"Parsing: {txt_file}")
print(f"Size: {os.path.getsize(txt_file)} bytes")

questions = parse_txt(txt_file)
print(f"\n>>> Intrebari extrase: {len(questions)}")

if questions:
    print("\n>>> Prima intrebare:")
    q = questions[0]
    print(f"  Text: {q['question'][:80]}")
    print(f"  Optiuni: {list(q['options'].keys())}")
    print(f"  Raspuns corect: {q['correct_answer']}")

    print("\n>>> Ultima intrebare:")
    q = questions[-1]
    print(f"  Text: {q['question'][:80]}")
    print(f"  Raspuns corect: {q['correct_answer']}")

    # Verifica daca toate au cel putin 3 optiuni
    sub3 = sum(1 for q in questions if len(q['options']) < 3)
    has4 = sum(1 for q in questions if len(q['options']) == 4)
    print(f"\n>>> Intrebari cu 4 optiuni: {has4}")
    print(f">>> Intrebari cu <3 optiuni: {sub3}")

    # Verifica daca sunt raspunsuri valide
    valid_answers = sum(1 for q in questions if q['correct_answer'] in ('a', 'b', 'c', 'd'))
    print(f">>> Raspunsuri valide (a/b/c/d): {valid_answers}")
