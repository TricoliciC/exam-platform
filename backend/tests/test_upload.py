import os
import sys
import json
import urllib.request
import urllib.parse

backend_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(backend_dir, 'test_exam.pdf')

pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 320>>stream
BT
/F1 12 Tf
50 750 Td
(1. Care este capitala Romaniei?) Tj
0 -20 Td
(a) Bucuresti) Tj
0 -20 Td
(b) Iasi) Tj
0 -20 Td
(c) Cluj) Tj
0 -20 Td
(d) Timisoara) Tj
0 -20 Td
(Correct: a) Tj
ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000056 00000 n
0000000103 00000 n
0000000200 00000 n
0000000570 00000 n
trailer<</Size 6/Root 1 0 R>>
startxref
640
%%EOF"""

with open(pdf_path, 'wb') as f:
    f.write(pdf_content)
print('1) PDF creat:', pdf_path, os.path.getsize(pdf_path), 'bytes')

print('2) Login admin...')
login_data = json.dumps({'email': 'admin@example.com', 'password': 'admin123'}).encode()
req = urllib.request.Request('http://localhost:5000/api/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read())
        token = body['access_token']
        print('   OK, token:', token[:30] + '...')
except urllib.error.HTTPError as e:
    print('   EROARE:', e.code, e.read().decode())
    sys.exit(1)

print('3) Get categories...')
req = urllib.request.Request('http://localhost:5000/api/exams/categories')
with urllib.request.urlopen(req) as resp:
    cats = json.loads(resp.read())['categories']
    print('   Categories:', [c['name'] for c in cats])

print('4) Upload PDF...')
boundary = '----WebKitFormBoundary' + os.urandom(8).hex()
parts = []
def add(name, value):
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
def add_file(name, filename, content):
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\nContent-Type: application/pdf\r\n\r\n'.encode())
    parts.append(content)
    parts.append(b'\r\n')

add('title', 'Test Examen')
add('description', 'Examen de test')
add('category_id', '1')
add_file('pdf_file', 'test_exam.pdf', pdf_content)
parts.append(f'--{boundary}--\r\n'.encode())
body = b''.join(parts)

req = urllib.request.Request(
    'http://localhost:5000/api/admin/exams',
    data=body,
    headers={
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'multipart/form-data; boundary=' + boundary
    }
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print('   OK:', json.dumps(result, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    print('   EROARE:', e.code)
    print('   Body:', e.read().decode())
    sys.exit(1)
