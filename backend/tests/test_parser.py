"""Unit tests for pdf_parser — covers multiple real-world PDF formats."""
import os
import sys
from fpdf import FPDF

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_parser import parse_pdf, parse_pdf_alternative


def make_pdf(path, lines):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in lines:
        pdf.cell(0, 10, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(path)


def assert_eq(actual, expected, label):
    status = "OK" if actual == expected else "FAIL"
    print(f"  [{status}] {label}: got={actual!r} expected={expected!r}")
    return actual == expected


passed = 0
total = 0


def test(name, func):
    global passed, total
    total += 1
    print(f"\n=== {name} ===")
    if func():
        passed += 1


# --- Test 1: Standard format with "Correct: x" marker ---
def test_standard():
    path = os.path.join(os.path.dirname(__file__), "t1.pdf")
    make_pdf(path, [
        "1. Care este capitala Frantei?",
        "a) Paris",
        "b) Londra",
        "c) Berlin",
        "d) Madrid",
        "Correct: a",
        "",
        "2. Cati ani are un deceniu?",
        "a) 5",
        "b) 10",
        "c) 100",
        "d) 50",
        "Correct: b",
    ])
    q = parse_pdf(path)
    ok = True
    ok &= assert_eq(len(q), 2, "question_count")
    if len(q) >= 1:
        ok &= assert_eq(q[0]['question'], "Care este capitala Frantei?", "q1_text")
        ok &= assert_eq(q[0]['correct_answer'], "a", "q1_correct")
    if len(q) >= 2:
        ok &= assert_eq(q[1]['correct_answer'], "b", "q2_correct")
    os.remove(path)
    return ok


# --- Test 2: Star marker on correct option ---
def test_star_marker():
    path = os.path.join(os.path.dirname(__file__), "t2.pdf")
    make_pdf(path, [
        "1. Cel mai mare fluviu din Europa?",
        "a) Dunarea",
        "b) Volga *",
        "c) Rin",
        "d) Sena",
    ])
    q = parse_pdf(path)
    ok = assert_eq(len(q), 1, "question_count")
    if q:
        ok &= assert_eq(q[0]['correct_answer'], "b", "star_marker")
        ok &= assert_eq(q[0]['options']['b'], "Volga", "star_cleaned")
    os.remove(path)
    return ok


# --- Test 3: Checkmark marker ---
def test_check_marker():
    path = os.path.join(os.path.dirname(__file__), "t3.pdf")
    make_pdf(path, [
        "1. Cel mai inalt munte?",
        "a) K2",
        "b) Everest",
        "c) Kilimanjaro",
        "d) Elbrus",
        "Raspuns: b",
    ])
    q = parse_pdf(path)
    ok = assert_eq(len(q), 1, "question_count")
    if q:
        ok &= assert_eq(q[0]['correct_answer'], "b", "raspuns_marker")
    os.remove(path)
    return ok


# --- Test 4: Question with multi-line text ---
def test_multiline_question():
    path = os.path.join(os.path.dirname(__file__), "t4.pdf")
    make_pdf(path, [
        "1. Care dintre urmatoarele orase",
        "este capitala Romaniei?",
        "a) Iasi",
        "b) Bucuresti",
        "c) Cluj",
        "d) Timisoara",
        "Correct: b",
    ])
    q = parse_pdf(path)
    ok = assert_eq(len(q), 1, "question_count")
    if q:
        ok &= assert_eq(q[0]['correct_answer'], "b", "multiline_correct")
    os.remove(path)
    return ok


# --- Test 5: Romanian "Corect:" marker ---
def test_corect_marker():
    path = os.path.join(os.path.dirname(__file__), "t5.pdf")
    make_pdf(path, [
        "1. 2 + 2 = ?",
        "a) 3",
        "b) 4",
        "c) 5",
        "d) 6",
        "Corect: b",
    ])
    q = parse_pdf(path)
    ok = assert_eq(len(q), 1, "question_count")
    if q:
        ok &= assert_eq(q[0]['correct_answer'], "b", "corect_marker")
    os.remove(path)
    return ok


# --- Test 6: No correct marker -> defaults to 'a' ---
def test_default_marker():
    path = os.path.join(os.path.dirname(__file__), "t6.pdf")
    make_pdf(path, [
        "1. Culoarea cerului?",
        "a) Albastru",
        "b) Verde",
        "c) Rosu",
        "d) Galben",
    ])
    q = parse_pdf(path)
    ok = assert_eq(len(q), 1, "question_count")
    if q:
        ok &= assert_eq(q[0]['correct_answer'], "a", "default_fallback")
    os.remove(path)
    return ok


# --- Test 7: Incomplete question (only 3 options) -> skipped ---
def test_incomplete_question():
    path = os.path.join(os.path.dirname(__file__), "t7.pdf")
    make_pdf(path, [
        "1. Intrebare incompleta?",
        "a) opt1",
        "b) opt2",
        "c) opt3",
        "Correct: a",
        "",
        "2. Intrebare completa?",
        "a) opt1",
        "b) opt2",
        "c) opt3",
        "d) opt4",
        "Correct: c",
    ])
    q = parse_pdf(path)
    ok = assert_eq(len(q), 1, "skipped_incomplete")
    if q:
        ok &= assert_eq(q[0]['question'], "Intrebare completa?", "only_complete_kept")
    os.remove(path)
    return ok


# --- Test 8: Alternative parser (per-line state machine) ---
def test_alternative_parser():
    path = os.path.join(os.path.dirname(__file__), "t8.pdf")
    make_pdf(path, [
        "1. Primul element din tabelul periodic?",
        "a) Heliu",
        "b) Hidrogen",
        "c) Litiu",
        "d) Carbon",
        "Correct: b",
    ])
    q = parse_pdf_alternative(path)
    ok = assert_eq(len(q), 1, "alt_question_count")
    if q:
        ok &= assert_eq(q[0]['correct_answer'], "b", "alt_correct")
    os.remove(path)
    return ok


test("Standard 'Correct: x' format", test_standard)
test("Star marker on correct option", test_star_marker)
test("Checkmark with 'Raspuns:' marker", test_check_marker)
test("Multi-line question text", test_multiline_question)
test("Romanian 'Corect:' marker", test_corect_marker)
test("Default to 'a' when no marker", test_default_marker)
test("Incomplete questions skipped", test_incomplete_question)
test("Alternative line-based parser", test_alternative_parser)

print(f"\n{'='*40}")
print(f"RESULT: {passed}/{total} tests passed")
sys.exit(0 if passed == total else 1)
