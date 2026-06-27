"""Debug: check questions in database."""
import os
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)

os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=" * 60)
print("Starting debug_questions.py")
print("=" * 60)

from app import app
from models import Question, Exam

with app.app_context():
    exams = Exam.query.all()
    print(f"Examene: {len(exams)}")
    for e in exams:
        print(f"  ID={e.id} | title={e.title!r} | questions={len(e.questions)}")

    questions = Question.query.order_by(Question.id).all()
    print(f"\nTotal intrebari: {len(questions)}")

    # Show first 10
    for q in questions[:10]:
        print(f"\nID={q.id} exam_id={q.exam_id} order={q.order}")
        print(f"  Q: {q.question_text[:80]}")
        print(f"  correct={q.correct_answer!r}")

    # Check for any with correct_answer not in 'abcd'
    bad = [q for q in questions if q.correct_answer not in ('a', 'b', 'c', 'd')]
    if bad:
        print(f"\nIntrebari cu correct_answer invalid: {len(bad)}")
        for q in bad[:5]:
            print(f"  ID={q.id} correct={q.correct_answer!r}")
    else:
        print("\nToate correct_answer sunt valide (a/b/c/d)")

    # Check distinct correct_answer values
    distinct = set(q.correct_answer for q in questions)
    print(f"\nValori distincte correct_answer: {distinct}")
