from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from database import db
from models import User, Category, Exam, Question, ExamAttempt, Answer, SiteSettings
from pdf_parser import parse_pdf, parse_txt
import os
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
exam_bp = Blueprint('exam', __name__)
admin_bp = Blueprint('admin', __name__)
user_bp = Blueprint('user', __name__)

# Auth routes
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    
    if not email or not username or not password:
        return jsonify({'error': 'Email, username și password sunt obligatorii'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email deja existent'}), 400
    
    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Utilizator înregistrat cu succes', 'user': user.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Email sau parolă incorectă'}), 401
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return jsonify({'user': user.to_dict()}), 200

# Exam routes
@exam_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.filter_by().all()
    return jsonify({'categories': [c.to_dict() for c in categories]}), 200

@exam_bp.route('/exams', methods=['GET'])
def get_exams():
    category_id = request.args.get('category_id')
    query = Exam.query.filter_by(is_active=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    exams = query.all()
    return jsonify({'exams': [e.to_dict() for e in exams]}), 200

@exam_bp.route('/exams/<int:exam_id>', methods=['GET'])
def get_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.order).all()
    return jsonify({
        'exam': exam.to_dict(),
        'questions': [q.to_dict() for q in questions]
    }), 200

@exam_bp.route('/attempts/start', methods=['POST'])
@jwt_required()
def start_attempt():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    exam_id = data.get('exam_id')
    
    exam = Exam.query.get_or_404(exam_id)
    attempt = ExamAttempt(exam_id=exam_id, user_id=user_id)
    db.session.add(attempt)
    db.session.commit()
    
    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.order).all()
    return jsonify({
        'attempt_id': attempt.id,
        'questions': [q.to_dict() for q in questions]
    }), 200

@exam_bp.route('/attempts/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_attempt(attempt_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    answers = data.get('answers', [])
    
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != user_id:
        return jsonify({'error': 'Nu aveți permisiune'}), 403
    
    attempt.completed_at = datetime.utcnow()
    total_questions = len(answers)
    correct_count = 0
    
    for ans in answers:
        question = Question.query.get(ans['question_id'])
        if question:
            is_correct = ans['selected_answer'] == question.correct_answer
            if is_correct:
                correct_count += 1
            answer = Answer(
                attempt_id=attempt_id,
                question_id=ans['question_id'],
                selected_answer=ans['selected_answer'],
                is_correct=is_correct
            )
            db.session.add(answer)
    
    attempt.total_questions = total_questions
    attempt.correct_answers = correct_count
    attempt.score = (correct_count / total_questions * 100) if total_questions > 0 else 0
    db.session.commit()
    
    return jsonify({'attempt': attempt.to_dict()}), 200

@exam_bp.route('/attempts/<int:attempt_id>', methods=['GET'])
@jwt_required()
def get_attempt(attempt_id):
    user_id = int(get_jwt_identity())
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != user_id:
        return jsonify({'error': 'Nu aveți permisiune'}), 403
    
    answers = Answer.query.filter_by(attempt_id=attempt_id).all()
    questions_data = []
    for ans in answers:
        question = Question.query.get(ans.question_id)
        if question:
            questions_data.append({
                'question': question.to_dict(),
                'selected_answer': ans.selected_answer,
                'is_correct': ans.is_correct
            })
    
    return jsonify({
        'attempt': attempt.to_dict(),
        'answers': questions_data
    }), 200

@exam_bp.route('/user/attempts', methods=['GET'])
@jwt_required()
def get_user_attempts():
    user_id = int(get_jwt_identity())
    attempts = ExamAttempt.query.filter_by(user_id=user_id).order_by(ExamAttempt.started_at.desc()).all()
    return jsonify({'attempts': [a.to_dict() for a in attempts]}), 200

# Admin routes
@admin_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Doar adminul poate crea categorii'}), 403
    
    data = request.get_json()
    category = Category(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(category)
    db.session.commit()
    
    return jsonify({'category': category.to_dict()}), 201

@admin_bp.route('/categories/<int:category_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def update_category(category_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Doar adminul poate modifica categorii'}), 403
    
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'DELETE':
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Categoria a fost ștearsă'}), 200
    
    data = request.get_json()
    category.name = data.get('name', category.name)
    category.description = data.get('description', category.description)
    db.session.commit()
    
    return jsonify({'category': category.to_dict()}), 200

@admin_bp.route('/exams', methods=['POST'])
@jwt_required()
def create_exam():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user.is_admin:
        return jsonify({'error': 'Doar adminul poate crea examene'}), 403

    # Accepta atat 'pdf_file' cat si 'txt_file' pentru compatibilitate
    uploaded_file = None
    field_name = None
    if 'pdf_file' in request.files:
        uploaded_file = request.files['pdf_file']
        field_name = 'pdf_file'
    elif 'txt_file' in request.files:
        uploaded_file = request.files['txt_file']
        field_name = 'txt_file'
    else:
        return jsonify({'error': 'Niciun fișier încărcat (pdf_file sau txt_file)'}), 400

    file = uploaded_file
    if file.filename == '':
        return jsonify({'error': 'Niciun fișier selectat'}), 400

    fname = file.filename.lower().strip()
    if not (fname.endswith('.pdf') or fname.endswith('.txt')):
        return jsonify({'error': 'Doar fișierele PDF sau TXT sunt acceptate'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Parseaza in functie de tip
    if fname.endswith('.pdf'):
        questions_data = parse_pdf(filepath)
    else:
        questions_data = parse_txt(filepath)

    if not questions_data:
        return jsonify({'error': 'Nu s-au putut extrage întrebări din fișier'}), 400

    exam = Exam(
        title=request.form['title'],
        description=request.form.get('description', ''),
        category_id=request.form['category_id'],
        pdf_file=filename,
        created_by=user_id
    )
    db.session.add(exam)
    db.session.commit()

    # Add questions
    for idx, q in enumerate(questions_data):
        question = Question(
            exam_id=exam.id,
            question_text=q['question'],
            option_a=q['options'].get('a', ''),
            option_b=q['options'].get('b', ''),
            option_c=q['options'].get('c', ''),
            option_d=q['options'].get('d', ''),
            correct_answer=q['correct_answer'],
            order=idx
        )
        db.session.add(question)

    db.session.commit()

    return jsonify({'exam': exam.to_dict(), 'questions_count': len(questions_data)}), 201

@admin_bp.route('/exams/<int:exam_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def update_exam(exam_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Doar adminul poate modifica examene'}), 403
    
    exam = Exam.query.get_or_404(exam_id)
    
    if request.method == 'DELETE':
        db.session.delete(exam)
        db.session.commit()
        return jsonify({'message': 'Examenul a fost șters'}), 200
    
    data = request.get_json()
    exam.title = data.get('title', exam.title)
    exam.description = data.get('description', exam.description)
    exam.is_active = data.get('is_active', exam.is_active)
    db.session.commit()
    
    return jsonify({'exam': exam.to_dict()}), 200

@admin_bp.route('/promote-admin', methods=['POST'])
@jwt_required()
def promote_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Doar adminul poate promovează alți admini'}), 403
    
    data = request.get_json()
    email = data.get('email')
    
    target_user = User.query.filter_by(email=email).first()
    if not target_user:
        return jsonify({'error': 'Utilizatorul nu există'}), 404
    
    target_user.is_admin = True
    db.session.commit()
    
    return jsonify({'message': f'{email} a fost promovat la admin', 'user': target_user.to_dict()}), 200

@admin_bp.route('/settings', methods=['GET', 'PUT'])
@jwt_required()
def site_settings():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Doar adminul poate modifica setările'}), 403
    
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'PUT':
        data = request.get_json()
        settings.site_name = data.get('site_name', settings.site_name)
        settings.logo_url = data.get('logo_url', settings.logo_url)
        settings.welcome_message = data.get('welcome_message', settings.welcome_message)
        settings.contact_email = data.get('contact_email', settings.contact_email)
        db.session.commit()
    
    return jsonify({'settings': settings.to_dict()}), 200

# Admin users management
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user.is_admin:
        return jsonify({'error': 'Doar adminul poate vedea utilizatorii'}), 403
    
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200

@admin_bp.route('/users/<int:user_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_user(user_id):
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    if not current_user.is_admin:
        return jsonify({'error': 'Doar adminul poate gestiona utilizatorii'}), 403
    
    target = User.query.get_or_404(user_id)
    
    if request.method == 'DELETE':
        if target.id == current_user.id:
            return jsonify({'error': 'Nu te poti sterge pe tine insuti'}), 400
        db.session.delete(target)
        db.session.commit()
        return jsonify({'message': 'Utilizatorul a fost sters'}), 200
    
    # PUT - update user
    data = request.get_json()
    if 'username' in data:
        target.username = data['username']
    if 'email' in data:
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email deja existent'}), 400
        target.email = data['email']
    if 'is_admin' in data:
        target.is_admin = bool(data['is_admin'])
    if 'password' in data and data['password']:
        target.set_password(data['password'])
    
    db.session.commit()
    return jsonify({'user': target.to_dict()}), 200

# User routes
@user_bp.route('/settings', methods=['GET'])
def get_public_settings():
    settings = SiteSettings.query.first()
    return jsonify({'settings': settings.to_dict() if settings else {}}), 200

# Temporary endpoint to create admin user
@auth_bp.route('/create-admin', methods=['POST'])
def create_admin():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({'error': 'Email, username și password sunt obligatorii'}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        # Update to admin if exists
        existing_user.is_admin = True
        existing_user.set_password(password)
        if username:
            existing_user.username = username
        db.session.commit()
        return jsonify({'message': 'Utilizator actualizat la admin', 'user': existing_user.to_dict()}), 200

    # Create new admin user
    user = User(email=email, username=username, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Admin user creat cu succes', 'user': user.to_dict()}), 201
