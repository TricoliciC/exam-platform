import os
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)

pdf.cell(0, 10, "1. Care este capitala Romaniei?", ln=True)
pdf.cell(0, 10, "a) Bucuresti", ln=True)
pdf.cell(0, 10, "b) Iasi", ln=True)
pdf.cell(0, 10, "c) Cluj", ln=True)
pdf.cell(0, 10, "d) Timisoara", ln=True)
pdf.cell(0, 10, "Correct: a", ln=True)
pdf.ln(5)

pdf.cell(0, 10, "2. Cati ani are o luna?", ln=True)
pdf.cell(0, 10, "a) 28", ln=True)
pdf.cell(0, 10, "b) 30", ln=True)
pdf.cell(0, 10, "c) 31", ln=True)
pdf.cell(0, 10, "d) 29", ln=True)
pdf.cell(0, 10, "Correct: b", ln=True)
pdf.ln(5)

pdf.cell(0, 10, "3. Care este cel mai mare ocean?", ln=True)
pdf.cell(0, 10, "a) Atlantic", ln=True)
pdf.cell(0, 10, "b) Indian", ln=True)
pdf.cell(0, 10, "c) Pacific *", ln=True)
pdf.cell(0, 10, "d) Arctic", ln=True)

pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "real_exam.pdf")
pdf.output(pdf_path)
print("PDF created:", pdf_path, os.path.getsize(pdf_path), "bytes")

import sys
import json
import urllib.request

print("Login admin...")
req = urllib.request.Request(
    "http://localhost:5000/api/auth/login",
    data=json.dumps({"email": "admin@example.com", "password": "admin123"}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read())["access_token"]
print("Token OK")

print("Upload PDF...")
boundary = "----FormBoundary" + os.urandom(4).hex()
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="title"\r\n\r\n'
    f"Test Examen Real\r\n"
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="description"\r\n\r\n'
    f"Examen de test cu PDF real\r\n"
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="category_id"\r\n\r\n'
    f"1\r\n"
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="pdf_file"; filename="real_exam.pdf"\r\n'
    f"Content-Type: application/pdf\r\n\r\n"
).encode() + pdf_bytes + f"\r\n--{boundary}--\r\n".encode()

req = urllib.request.Request(
    "http://localhost:5000/api/admin/exams",
    data=body,
    headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "multipart/form-data; boundary=" + boundary
    }
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print("OK:", json.dumps(result, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    print("ERROR:", e.code, e.read().decode())
