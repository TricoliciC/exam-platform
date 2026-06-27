import re

try:
    import pypdf as _pdf_lib
    _PDF_LIB_NAME = 'pypdf'
except ImportError:
    try:
        import PyPDF2 as _pdf_lib
        _PDF_LIB_NAME = 'PyPDF2'
    except ImportError:
        raise ImportError(
            "Nicio biblioteca PDF instalata. Ruleaza: pip install pypdf PyPDF2"
        )


def _extract_text(filepath):
    text_parts = []
    with open(filepath, 'rb') as f:
        reader = _pdf_lib.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text() or ''
            text_parts.append(page_text)
    return '\n'.join(text_parts)


def _normalize(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{2,}', '\n', text)
    lines = [ln.rstrip() for ln in text.split('\n')]
    text = '\n'.join(lines)
    text = re.sub(r'(?<!\n)\n(?!\n)', '\n', text)
    return text.strip()


def _find_correct_marker(block):
    patterns = [
        r'(?im)^\s*(?:correct|corect|raspuns|answer)\s*[:\-]?\s*([a-d])\b',
        r'(?im)^\s*\*\s*([a-d])\b',
        r'(?im)\b([a-d])\s*\)?\s*[\*✓✔]\s*$',
    ]
    for pat in patterns:
        m = re.search(pat, block)
        if m:
            return m.group(1).lower()
    for letter in ('a', 'b', 'c', 'd'):
        if re.search(rf'(?im)^\s*{letter}\)\s*[^\n]*\*\s*$', block) or \
           re.search(rf'(?im)^\s*{letter}\)\s*[^\n]*[✓✔]\s*$', block):
            return letter
    return None


def _clean_option(text):
    return re.sub(r'[\*✓✔]\s*$', '', text).strip()


def _parse_block(block):
    lines = [ln.strip() for ln in block.split('\n') if ln.strip()]
    if not lines:
        return None

    first = lines[0]
    q_match = re.match(r'^\d+[\.\)]\s*(.+)$', first)
    if not q_match:
        return None

    question_text = q_match.group(1).strip()
    option_lines = lines[1:]

    options = {}
    option_re = re.compile(r'^([a-d])\s*[\)\.]\s*(.+)$', re.IGNORECASE)
    for line in option_lines:
        m = option_re.match(line)
        if m:
            letter = m.group(1).lower()
            text = _clean_option(m.group(2).strip())
            options[letter] = text
        else:
            if options:
                last_letter = max(options.keys(), key=lambda k: ord(k))
                options[last_letter] = (options[last_letter] + ' ' + line).strip()

    if len(options) < 4:
        return None
    for letter in ('a', 'b', 'c', 'd'):
        if letter not in options:
            return None

    correct = _find_correct_marker(block)
    if not correct:
        correct = 'a'

    return {
        'question': question_text,
        'options': {
            'a': options['a'],
            'b': options['b'],
            'c': options['c'],
            'd': options['d'],
        },
        'correct_answer': correct,
    }


def parse_pdf(filepath):
    try:
        raw_text = _extract_text(filepath)
    except Exception as e:
        print(f"[pdf_parser] Extraction error: {e}")
        return []

    text = _normalize(raw_text)
    if not text:
        return []

    blocks = re.split(r'\n(?=\d+[\.\)]\s)', text)
    questions = []
    for block in blocks:
        if not block.strip():
            continue
        parsed = _parse_block(block)
        if parsed:
            questions.append(parsed)

    return questions


def parse_pdf_alternative(filepath):
    try:
        raw_text = _extract_text(filepath)
    except Exception as e:
        print(f"[pdf_parser] Alt extraction error: {e}")
        return []

    text = _normalize(raw_text)
    if not text:
        return []

    questions = []
    current = None
    current_raw_lines = []
    option_re = re.compile(r'^([a-d])\s*[\)\.]\s*(.+)$', re.IGNORECASE)
    question_re = re.compile(r'^\d+[\.\)]\s*(.+)$')

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        if question_re.match(line):
            if current and len(current['options']) >= 4:
                correct = _find_correct_marker('\n'.join(current_raw_lines))
                if correct:
                    current['correct_answer'] = correct
                questions.append(current)
            current = {
                'question': question_re.match(line).group(1).strip(),
                'options': {},
                'correct_answer': 'a',
            }
            current_raw_lines = [line]
        elif current is not None:
            current_raw_lines.append(line)
            m = option_re.match(line)
            if m:
                current['options'][m.group(1).lower()] = _clean_option(m.group(2).strip())

    if current and len(current['options']) >= 4:
        correct = _find_correct_marker('\n'.join(current_raw_lines))
        if correct:
            current['correct_answer'] = correct
        questions.append(current)

    return questions


def parse_txt(filepath):
    """Parseaza un fisier .txt care contine intrebari in formatul standard.

    Format asteptat (flexibil):
        1. Intrebare?
        a) Optiune 1
        b) Optiune 2
        c) Optiune 3
        d) Optiune 4
        Correct: a

        2. Alta intrebare?
        ...
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='cp1252') as f:
                text = f.read()
        except Exception as e:
            print(f"[pdf_parser] TXT read error: {e}")
            return []
    except Exception as e:
        print(f"[pdf_parser] TXT read error: {e}")
        return []

    # Elimina comentarii (linii care incep cu #)
    lines_clean = []
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        # Elimina si sectiunile de tip "--- INTREBARE 1 ---"
        if re.match(r'^---\s*INTREBARE\s+\d+\s*---$', stripped, re.IGNORECASE):
            continue
        lines_clean.append(line)

    text = '\n'.join(lines_clean)
    text = _normalize(text)
    if not text:
        return []

    return parse_pdf_alternative_from_text(text)


def parse_pdf_alternative_from_text(text):
    """Varianta a lui parse_pdf_alternative care primeste textul direct."""
    questions = []
    current = None
    current_raw_lines = []
    option_re = re.compile(r'^([a-d])\s*[\)\.]\s*(.+)$', re.IGNORECASE)
    question_re = re.compile(r'^\d+[\.\)]\s*(.+)$')

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        if question_re.match(line):
            if current and len(current['options']) >= 3:
                correct = _find_correct_marker('\n'.join(current_raw_lines))
                if correct:
                    current['correct_answer'] = correct
                # Completeaza daca lipseste
                for letter in ('a', 'b', 'c', 'd'):
                    if letter not in current['options']:
                        current['options'][letter] = '[nespecificat]'
                questions.append(current)
            current = {
                'question': question_re.match(line).group(1).strip(),
                'options': {},
                'correct_answer': 'a',
            }
            current_raw_lines = [line]
        elif current is not None:
            current_raw_lines.append(line)
            m = option_re.match(line)
            if m:
                current['options'][m.group(1).lower()] = _clean_option(m.group(2).strip())

    if current and len(current['options']) >= 3:
        correct = _find_correct_marker('\n'.join(current_raw_lines))
        if correct:
            current['correct_answer'] = correct
        for letter in ('a', 'b', 'c', 'd'):
            if letter not in current['options']:
                current['options'][letter] = '[nespecificat]'
        questions.append(current)

    return questions
