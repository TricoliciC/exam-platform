"""
Helper script imbunatatit: pune PDF-ul in folderul user_uploads/, ruleaza acest script,
si el iti creeaza un fisier .txt gata de completat manual.

Imbunatatiri vs versiunea anterioara:
- Curata spatiile ciudate din PDF (ex: "fapt ei" -> "faptei")
- Accepta intrebari cu 3 SAU 4 optiuni (completeaza cu placeholder daca lipseste)
- Pune "Correct: ?" pentru toate raspunsurile (TU le completezi manual)
- Pastreaza TOATE intrebarile, nu le sari
- Detecteaza marcatori de raspuns (*, **, Raspuns:, Correct:) daca exista

Output: user_uploads/<nume_pdf>_extracted.txt
"""
import os
import sys
import re
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import pypdf as _pdf_lib
except ImportError:
    import PyPDF2 as _pdf_lib

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_uploads")


def extract_text(filepath):
    parts = []
    with open(filepath, "rb") as f:
        reader = _pdf_lib.PdfReader(f)
        for page in reader.pages:
            t = page.extract_text() or ""
            parts.append(t)
    return "\n".join(parts)


def normalize(text):
    """Curata textul extras din PDF - versiune conservativa."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Strategie: uneste spatiile doar in 2 cazuri clare:
    # 1. Cand o diacritica (ă, â, î, ș, ț) este separata gresit:
    #    "săv ârşirii" -> "săvârşirii"  (litera diacritica incepe un cuvant nou)
    #    "fapt ei"    nu e afectat
    diacritics = "ăâîșțĂÂÎȘȚ"
    # Caz: litera normala + spatiu + diacritica (ex: "v â" -> "vâ")
    text = re.sub(rf'(?<=[a-zA-Z]) (?=[{diacritics}])', '', text)
    # Caz: diacritica + spatiu + litera normala (ex: "ă i" -> "ăi")
    text = re.sub(rf'(?<=[{diacritics}]) (?=[a-zA-Z])', '', text)
    # Caz: diacritica + spatiu + diacritica (ex: "î ă" -> "îă")
    text = re.sub(rf'(?<=[{diacritics}]) (?=[{diacritics}])', '', text)

    # 2. Uneste "cuvinte" foarte scurte (1-2 litere) urmate de alt text:
    #    "fapt ei" -> "faptei"  (cuvant de 2 litere lipit de urmatorul)
    #    "de o"    -> "deo"     (prepozitie de 2 litere)
    #    Pastram totusi: "a b" cu ambele > 2 litere, "cel mai" etc.
    # Aplicam de mai multe ori pt. cazuri ca "fapt ei se" -> "faptei se"
    for _ in range(3):
        text = re.sub(
            r'\b([a-zA-ZăâîșțĂÂÎȘȚ]{1,2})\s+(?=[a-zA-ZăâîșțĂÂÎȘȚ])',
            r'\1',
            text
        )

    # 3. Elimina spatiile multiple si tab-urile
    text = re.sub(r"[ \t]+", " ", text)

    # 4. Elimina liniile goale multiple
    text = re.sub(r"\n{2,}", "\n", text)

    # 5. Strip pe fiecare linie
    lines = [ln.strip() for ln in text.split("\n")]
    return "\n".join(lines).strip()


def find_correct_marker(block):
    """Cauta marker de raspuns corect in blocul de intrebare."""
    patterns = [
        r"(?im)^\s*(?:correct|corect|raspuns|answer|răspuns|corectul este|varianta corecta)\s*[:\-=]?\s*([a-d])\b",
        r"(?im)^\s*\*\s*([a-d])\s*$",
        r"(?im)^\s*([a-d])\s*[\*]+\s*$",
    ]
    for pat in patterns:
        m = re.search(pat, block)
        if m:
            return m.group(1).lower()
    # Verifica daca vreo optiune are * la final
    for letter in ("a", "b", "c", "d"):
        if re.search(rf"(?im)^\s*{letter}\)\s*[^\n]*\*+\s*$", block) or \
           re.search(rf"(?im)^\s*{letter}\)\s*[^\n]*[\u2713\u2714\u2715\u2716\u2717\u2718\u2719\u271a]\s*$", block):
            return letter
    return None


def clean_option(text):
    """Elimina marker-e de la finalul optiunii (*, bifa)."""
    return re.sub(r"[\*\u2713\u2714\u2715\u2716\u2717\u2718\u2719\u271a]+\s*$", "", text).strip()


def parse_questions(text):
    """Parseaza textul intr-o lista de intrebari in format standard."""
    questions = []
    # Imparte in blocuri la intalnirea unui nou "1." "2." etc.
    blocks = re.split(r"\n(?=\d+[\.\)]\s)", text)
    option_re = re.compile(r"^([a-d])\s*[\)\.]\s*(.+)$", re.IGNORECASE)
    question_re = re.compile(r"^\d+[\.\)]\s*(.+)")

    skipped = []

    for block in blocks:
        if not block.strip():
            continue
        lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue

        # Filtreaza antetele de sectiune (ex: "Drept penal")
        first = lines[0]
        m = question_re.match(first)
        if not m:
            # Posibil antet de sectiune
            if not option_re.match(first) and len(first) < 60:
                # Probabil antet, incearca sa gasesti prima intrebare in block
                for line in lines:
                    if question_re.match(line):
                        m = question_re.match(line)
                        lines = lines[lines.index(line):]
                        break
                if not m:
                    continue
            else:
                continue

        question_text = m.group(1).strip()

        # Ignora daca e evident antet (contine "Drept", "Legea", "Codul" fara "?" la final)
        section_keywords = ["drept", "codul", "legea", "secțiunea", "sectiunea", "capitolul", "tematica"]
        is_section = any(kw in question_text.lower() for kw in section_keywords) and not question_text.endswith("?")
        if is_section:
            continue

        # Aduna optiunile (pot fi pe linii multiple)
        options = {}
        option_started = False
        for line in lines[1:]:
            om = option_re.match(line)
            if om:
                letter = om.group(1).lower()
                options[letter] = clean_option(om.group(2).strip())
                option_started = True
            elif option_started and options:
                # Continuare a optiunii anterioare (text pe mai multe randuri)
                last = max(options.keys(), key=lambda k: ord(k))
                options[last] = (options[last] + " " + line).strip()

        if not options:
            skipped.append(("fara_optiuni", question_text[:60]))
            continue

        if len(options) < 3:
            skipped.append(("prea_putine_optiuni", question_text[:60]))
            continue

        # Completeaza cu placeholder daca lipseste 'd'
        if "d" not in options:
            options["d"] = "[adauga optiunea d aici]"

        # Verifica daca toate cele 4 litere sunt prezente
        for letter in ("a", "b", "c", "d"):
            if letter not in options:
                options[letter] = f"[optiune {letter} lipsa]"

        correct = find_correct_marker(block)

        questions.append({
            "question": question_text,
            "options": options,
            "correct": correct,  # None daca nu a fost gasit
            "needs_answer": correct is None,
        })

    return questions, skipped


def write_output(questions, skipped, output_path, pdf_name):
    """Scrie intrebarile in formatul asteptat de parser-ul de pe site."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("#" * 70 + "\n")
        f.write(f"# Fisier generat din: {pdf_name}\n")
        f.write(f"# Total intrebari extrase: {len(questions)}\n")
        if skipped:
            f.write(f"# Intrebari sarite: {len(skipped)}\n")
        f.write("#" * 70 + "\n\n")
        f.write("# INSTRUCTIUNI:\n")
        f.write("# 1. Pentru fiecare intrebare, cauta 'Correct: ?' si inlocuieste '?'\n")
        f.write("#    cu litera raspunsului corect (a, b, c, sau d).\n")
        f.write("# 2. Daca lipseste optiunea d), completeaz-o unde scrie '[adauga...]'.\n")
        f.write("# 3. Daca textul intrebarii are caractere ciudate, corecteaza manual.\n")
        f.write("# 4. Cand ai terminat, copiaza TOT continutul intr-un document Word,\n")
        f.write("#    formateaza si salveaza ca PDF. Apoi incarca PDF-ul pe site.\n")
        f.write("#" * 70 + "\n\n")

        # Grupeaza pe sectiuni (daca detectam antetele)
        for idx, q in enumerate(questions, 1):
            f.write(f"--- INTREBARE {idx} ---\n")
            f.write(f"{idx}. {q['question']}\n")
            for letter in ("a", "b", "c", "d"):
                f.write(f"{letter}) {q['options'][letter]}\n")
            if q["correct"]:
                f.write(f"Correct: {q['correct']}\n\n")
            else:
                f.write(f"Correct: ?  <-- COMPLETEAZA MANUAL\n\n")

        if skipped:
            f.write("\n" + "=" * 70 + "\n")
            f.write(f"# INTREBARI SARIITE ({len(skipped)}):\n")
            f.write("=" * 70 + "\n")
            for reason, qtext in skipped[:50]:
                f.write(f"  - [{reason}] {qtext}\n")
            if len(skipped) > 50:
                f.write(f"  ... si inca {len(skipped) - 50} intrebari sarite\n")

    return len(questions)


def main():
    if not os.path.isdir(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    pdfs = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(".pdf")]
    if not pdfs:
        print(f"Niciun PDF gasit in {UPLOAD_DIR}")
        print("Pune un fisier .pdf acolo si ruleaza din nou.")
        sys.exit(1)

    for pdf_name in pdfs:
        pdf_path = os.path.join(UPLOAD_DIR, pdf_name)
        print(f"\n=== Procesare: {pdf_name} ===")
        try:
            raw = extract_text(pdf_path)
        except Exception as e:
            print(f"EROARE la citire: {e}")
            continue

        if not raw.strip():
            print("PDF-ul nu are text extras (probabil e scanat/imagine).")
            print("Trebuie sa-l convertesti manual in PDF cu text selectabil.")
            continue

        text = normalize(raw)
        questions, skipped = parse_questions(text)

        out_name = os.path.splitext(pdf_name)[0] + "_extracted.txt"
        out_path = os.path.join(UPLOAD_DIR, out_name)
        count = write_output(questions, skipped, out_path, pdf_name)

        print(f"\n>>> REZULTAT:")
        print(f">>> Intrebari extrase: {count}")
        print(f">>> Intrebari sarite: {len(skipped)}")
        print(f">>> Fisiere care TREBUIE completate manual: {sum(1 for q in questions if q['needs_answer'])}")
        print(f">>> Fisiere cu raspuns deja marcat in PDF: {sum(1 for q in questions if not q['needs_answer'])}")
        print(f">>> Fisier salvat: {out_path}")

        # Afiseaza primele 30 de linii ca previzualizare
        print(f"\n=== PREVIZUALIZARE (primele 30 linii) ===")
        with open(out_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 30:
                    break
                print(line.rstrip())
        print(f"=== (vezi fisierul complet: {out_path}) ===\n")

    print("=" * 70)
    print("GATA. Urmatorii pasi:")
    print("1. Deschide fisierul .txt generat in Notepad/VSCode")
    print("2. Cauta toate 'Correct: ?' si completeaza cu litera corecta")
    print("3. Verifica daca intrebarile au fost extrase corect (text curat)")
    print("4. Selecteaza tot continutul, copiaza in Word/Docs")
    print("5. Salveaza ca PDF si incarca pe site")
    print("=" * 70)


if __name__ == "__main__":
    main()
