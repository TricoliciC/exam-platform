"""Verifica ce examene sunt in DB."""
import os
import io
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from app import app
from models import Exam, Category, Question

with app.app_context():
    print("=== EXAMENE IN DB ===")
    exams = Exam.query.all()
    if not exams:
        print("  Nu exista examene!")
    for e in exams:
        q_count = Question.query.filter_by(exam_id=e.id).count()
        cat = Category.query.get(e.category_id)
        cat_name = cat.name if cat else "NONE"
        print(f"  ID={e.id} | title='{e.title}' | active={e.is_active} | category_id={e.category_id} ({cat_name}) | questions={q_count}")

    print()
    print("=== CATEGORII ===")
    for c in Category.query.all():
        ce = Exam.query.filter_by(category_id=c.id, is_active=True).count()
        print(f"  ID={c.id} | name='{c.name}' | examene_active={ce}")
