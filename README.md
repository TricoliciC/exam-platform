# Platformă de Testare - Exam Platform

O platformă completă pentru testarea cunoștințelor cu încărcare de examene din fișiere PDF.

## Funcționalități

### Pentru Utilizatori
- **Înregistrare și Login** - Sistem de autentificare securizat
- **Vizualizare Examene** - Browse examene organizate pe categorii
- **Testare Interactivă** - Interfață prietenoasă pentru răspunderea la întrebări
- **Rezultate Detaliate** - Vizualizarea scorului, răspunsurilor corecte/greșite și explicații
- **Istoric Încercări** - Vizualizarea tuturor încercărilor anterioare

### Pentru Admin
- **Gestionare Categorii** - Creare, editare și ștergere categorii de examene
- **Încărcare Examene** - Upload fișiere PDF cu întrebări și variante de răspuns
- **Gestionare Examene** - Editare titlu, descriere, activare/dezactivare
- **Setări Site** - Modificare nume site, logo, mesaj de bun venit, email contact
- **Promovare Admin** - Promovarea utilizatorilor existenți la rol de admin

## Structură Proiect

```
exam-platform/
├── backend/
│   ├── app.py              # Aplicația Flask principală
│   ├── database.py         # Inițializare baza de date
│   ├── models.py           # Modele SQLAlchemy
│   ├── routes.py           # Rute API
│   ├── pdf_parser.py       # Parser pentru fișiere PDF
│   ├── requirements.txt     # Dependințe Python
│   └── .env                # Variabile de mediu
├── frontend/
│   ├── src/
│   │   ├── components/     # Componente React (Navbar)
│   │   ├── pages/          # Pagini React
│   │   ├── App.jsx         # Componenta principală
│   │   ├── main.jsx        # Entry point
│   │   └── index.css       # Stiluri globale
│   ├── index.html          # HTML principal
│   ├── vite.config.js      # Configurare Vite
│   └── package.json        # Dependințe Node.js
└── README.md               # Acest fișier
```

## Instalare și Rulare

### Prerechizite
- Python 3.8+
- Node.js 16+ și npm
- Git (opțional)

### Backend (Flask)

1. Navighează în directorul backend:
```bash
cd backend
```

2. Creează un mediu virtual:
```bash
python -m venv venv
```

3. Activează mediul virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalează dependențele:
```bash
pip install -r requirements.txt
```

5. Configurează variabilele de mediu în `.env`:
```
SECRET_KEY=cheia-ta-secreta-aici
ADMIN_EMAIL=admin@example.com
DATABASE_URL=sqlite:///exam_platform.db
```

6. Rulează serverul Flask:
```bash
python app.py
```

Serverul va rula pe `http://localhost:5000`

### Frontend (React)

1. Navighează în directorul frontend:
```bash
cd frontend
```

2. Instalează dependențele:
```bash
npm install
```

3. Rulează serverul de dezvoltare:
```bash
npm run dev
```

Frontend-ul va rula pe `http://localhost:3000`

## Format Fișiere PDF

Pentru ca parser-ul să extragă corect întrebările, fișierele PDF trebuie să urmeze formatul:

```
1. Textul întrebării
a) Varianta A
b) Varianta B
c) Varianta C
d) Varianta D
Correct: a
```

Alternativ, răspunsul corect poate fi marcat cu:
- `Correct: a` sau `Corect: a`
- `Answer: a` sau `Raspuns: a`
- `*` sau `✓` lângă varianta corectă

## Configurare Admin

Adminul este definit prin email-ul specificat în fișierul `.env` (variabila `ADMIN_EMAIL`).

### Promovare Utilizator la Admin

1. Loghează-te ca admin
2. Navighează la Admin → Setări Site
3. Introdu email-ul utilizatorului pe care vrei să-l promovezi
4. Click pe "Promovează la Admin"

## Utilizare

### Pentru Utilizatori
1. Înregistrează-te pe platformă
2. Navighează la pagina principală pentru a vedea categoriile
3. Selectează o categorie și alege un examen
4. Click pe "Începe Testul"
5. Răspunde la întrebări în limita de timp
6. Vizualizează rezultatul detaliat

### Pentru Admin
1. Loghează-te cu contul de admin
2. Navighează la panoul Admin
3. Creează categorii pentru organizarea examenelor
4. Încarcă fișiere PDF cu examene
5. Modifică setările site-ului după nevoie

## API Endpoints

### Auth
- `POST /api/auth/register` - Înregistrare utilizator
- `POST /api/auth/login` - Login utilizator
- `GET /api/auth/me` - Obține utilizatorul curent

### Exams
- `GET /api/exams/categories` - Obține toate categoriile
- `GET /api/exams/exams` - Obține toate examenele
- `GET /api/exams/exams/:id` - Obține detaliile unui examen
- `POST /api/exams/attempts/start` - Începe o încercare
- `POST /api/exams/attempts/:id/submit` - Trimite răspunsurile
- `GET /api/exams/attempts/:id` - Obține rezultatul unei încercări
- `GET /api/exams/user/attempts` - Obține încercările utilizatorului

### Admin
- `POST /api/admin/categories` - Creează categorie
- `PUT /api/admin/categories/:id` - Actualizează categorie
- `DELETE /api/admin/categories/:id` - Șterge categorie
- `POST /api/admin/exams` - Încarcă examen
- `PUT /api/admin/exams/:id` - Actualizează examen
- `DELETE /api/admin/exams/:id` - Șterge examen
- `POST /api/admin/promote-admin` - Promovează utilizator la admin
- `GET /api/admin/settings` - Obține setările site-ului
- `PUT /api/admin/settings` - Actualizează setările site-ului

## Dezvoltare

### Adăugare Funcționalități Noi

Proiectul este structurat modular pentru a facilita adăugarea de noi funcționalități:

1. **Backend**: Adaugă noi rute în `routes.py` și modele în `models.py`
2. **Frontend**: Adaugă noi componente în `src/components/` și pagini în `src/pages/`
3. **Styling**: Modifică `src/index.css` pentru stiluri globale

### Modificări

Da, poți face modificări în continuare în acest program! Proiectul este:
- Open source și complet personalizabil
- Documentat cu comentarii
- Structurat pe module pentru ușurința în modificare

## Suport

Pentru întrebări sau probleme, verifică:
1. Documentația de mai sus
2. Logurile serverului Flask
3. Consolele browserului pentru erori frontend

## Licență

Acest proiect este creat pentru scopuri educaționale și poate fi modificat și distribuit liber.
