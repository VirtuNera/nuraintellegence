from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, db
from backend.models import User, Student, Teacher, Admin, Subject, Topic, Quiz, QuizResponse, PerformanceTrend, QuestionSet, Question, AdaptiveQuizSession
from backend.ai_service import NuraAI
from backend.fast_ai_service import fast_ai
from backend.fast_prediction_service import fast_prediction_service
from backend.unified_quiz_engine import UnifiedQuizEngine
from backend.database_optimizations import DatabaseOptimizer
from backend.performance_cache import cache
from backend.topic_prediction_service import topic_prediction_service
import json
import uuid
import os
from datetime import datetime, timedelta

# Initialize AI service and quiz engines
nura_ai = NuraAI()
quiz_engine = UnifiedQuizEngine()

# Define hidden subjects globally
HIDDEN_SUBJECTS = [
    'Mathematics', 'Science', 'English', 'History', 'Geography',
    'PISA Mathematics', 'Question Set', 'Performance Log'
]


@app.route('/')
def landing():
    """Landing page with introduction to Nura AI"""
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for learners and educators"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            # Redirect based on role
            if user.role == 'student':
                return redirect(url_for('learner_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('educator_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page for new users"""
    if request.method == 'POST':
        # Get common fields
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')

        # Validation
        if not all([full_name, email, password, confirm_password, role]):
            flash('Please fill in all fields', 'error')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')

        # Create user
        user = User()
        user.full_name = full_name
        user.email = email
        user.password_hash = generate_password_hash(password)
        user.role = role
        db.session.add(user)
        db.session.flush()  # Get the user ID

        # Create role-specific profile
        if role == 'student':
            student = Student()
            student.user_id = user.id
            student.grade_level = "Not specified"  # Provide default value
            student.preferred_subjects = []  # Empty array instead of None
            db.session.add(student)

        elif role == 'teacher':
            school_name = request.form.get('school_name')
            subjects_taught = request.form.getlist('subjects_taught')

            educator = Teacher()
            educator.user_id = user.id
            educator.school_name = school_name
            educator.subjects_taught = subjects_taught
            db.session.add(educator)

        try:
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating account: {str(e)}")
            flash(
                'An error occurred while creating your account. Please try again.',
                'error')
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('landing'))


@app.route('/learner/dashboard')
@login_required
def learner_dashboard():
    """Learner dashboard with analytics and AI assistant"""
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('landing'))

    learner = current_user.student_profile

    # Get performance data using optimized queries with caching
    cache_key = f"dashboard_data_{learner.student_id}"
    performance_data = cache.get(cache_key)
    if not performance_data:
        performance_data = DatabaseOptimizer.get_student_performance_optimized(
            learner.student_id)
        cache.set(cache_key, performance_data, ttl=300)  # 5 minute cache

    # Get AI feedback using fast service for better performance
    ai_feedback = fast_ai.generate_learner_feedback(learner.student_id)

    # Get available subjects using optimized query with caching
    cache_key = "available_subjects"
    subjects = cache.get(cache_key)
    if not subjects:
        subjects = Subject.query.all()
        cache.set(cache_key, subjects, ttl=600)  # 10 minute cache

    return render_template('learner_dashboard.html',
                           learner=learner,
                           performance_data=performance_data,
                           ai_feedback=ai_feedback,
                           subjects=subjects)


@app.route('/educator/dashboard')
@login_required
def educator_dashboard():
    """Educator dashboard with class overview"""
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('landing'))

    educator = current_user.teacher_profile

    # Get class overview data
    class_data = get_class_overview_data()

    # Get learners performance for traffic light system
    students_performance = get_learners_traffic_light_data()

    return render_template('educator_dashboard.html',
                           educator=educator,
                           class_data=class_data,
                           students_performance=students_performance)


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard with comprehensive system analytics"""
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('landing'))

    admin = current_user.admin_profile

    # Get comprehensive admin analytics using optimized queries
    metrics = DatabaseOptimizer.get_dashboard_metrics_optimized()

    # Add additional metrics that admin dashboard expects
    from datetime import datetime, timedelta
    total_users = User.query.count()
    total_learners = User.query.filter_by(role='student').count()
    total_educators = User.query.filter_by(role='teacher').count()
    total_admins = User.query.filter_by(role='admin').count()

    analytics_data = {
        **metrics, 'total_users': total_users,
        'total_learners': total_learners,
        'total_educators': total_educators,
        'total_admins': total_admins,
        'total_subjects': Subject.query.count(),
        'total_topics': Topic.query.count(),
        'total_questions': Question.query.count(),
        'total_quizzes': Quiz.query.count(),
        'total_quiz_responses': QuizResponse.query.count()
    }

    return render_template('admin_dashboard.html',
                           admin=admin,
                           analytics=analytics_data)


@app.route('/quiz/start/<topic_id>')
@app.route('/quiz/start/<topic_id>/<difficulty>')
@login_required
def start_quiz(topic_id, difficulty=None):
    """Start a new quiz for the given topic and difficulty level"""
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('landing'))

    learner = current_user.student_profile
    topic = Topic.query.filter_by(topic_id=topic_id).first()

    if not topic:
        flash('Topic not found', 'error')
        return redirect(url_for('subject_selection'))

    # If no difficulty specified, try to find an appropriate difficulty level
    if not difficulty:
        # Check if we have any question sets for this topic
        available_sets = QuestionSet.query.filter_by(topic_id=topic_id).all()
        if not available_sets:
            flash('No questions available for this topic', 'error')
            return redirect(url_for('subject_selection'))

        # For topic predictions, automatically select Medium difficulty if available
        # Otherwise, use the first available difficulty
        preferred_difficulties = [
            'Medium', 'Easy', 'Hard', 'Very Easy', 'Very Hard'
        ]
        selected_set = None

        for pref_diff in preferred_difficulties:
            for question_set in available_sets:
                if question_set.difficulty_level == pref_diff:
                    selected_set = question_set
                    difficulty = pref_diff
                    break
            if selected_set:
                break

        # If no match found, use the first available set
        if not selected_set:
            selected_set = available_sets[0]
            difficulty = selected_set.difficulty_level

        # Continue with the selected difficulty
        question_set = selected_set
    else:
        # Get questions for the specified difficulty level
        question_set = QuestionSet.query.filter_by(
            topic_id=topic_id, difficulty_level=difficulty).first()

    if not question_set:
        flash(f'No questions available for {difficulty} level', 'error')
        return redirect(url_for('subject_selection'))

    # Get questions from the set
    questions = Question.query.filter_by(
        set_id=question_set.question_set_id).all()

    if not questions:
        flash('No questions available for this quiz', 'error')
        return redirect(url_for('subject_selection'))

    # Format quiz data
    quiz_data = {
        'quiz_id':
        str(uuid.uuid4()),
        'topic_id':
        topic_id,
        'difficulty_level':
        difficulty,
        'question_set_id':
        question_set.question_set_id,
        'questions': [{
            'question_id': q.question_id,
            'description': q.description,
            'options': q.options,
            'correct_option': q.correct_option,
            'marks_worth': q.marks_worth,
            'image_url': q.image_url
        } for q in questions],
        'total_marks':
        sum(q.marks_worth for q in questions),
        'time_limit':
        len(questions) * 60  # 1 minute per question
    }

    # Store quiz in session
    session['current_quiz'] = quiz_data

    return render_template('quiz.html', quiz=quiz_data, topic=topic)


@app.route('/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    """Submit quiz answers and get results"""
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('landing'))

    quiz_data = session.get('current_quiz')
    if not quiz_data:
        flash('No active quiz found', 'error')
        return redirect(url_for('learner_dashboard'))

    # Process quiz submission
    answers = request.form.to_dict()
    learner = current_user.student_profile

    print(f"Form data received: {answers}")

    # Calculate results and store in database
    results = process_quiz_submission_direct(learner.student_id, quiz_data,
                                             answers)

    # Generate AI feedback (only if submission was successful)
    ai_feedback = None
    if results and not results.get('error'):
        ai_feedback = nura_ai.generate_quiz_feedback(learner.student_id,
                                                     results)
    else:
        ai_feedback = {
            "feedback": "Unable to generate feedback due to submission error.",
            "recommendations": []
        }

    # Clear session
    session.pop('current_quiz', None)

    return render_template('quiz_result.html',
                           results=results,
                           ai_feedback=ai_feedback)


@app.route('/api/performance/<student_id>')
@login_required
def get_performance_api(student_id):
    """API endpoint to get learner performance data"""
    if current_user.role != 'teacher' and current_user.student_profile.student_id != student_id:
        return jsonify({'error': 'Access denied'}), 403

    performance_data = get_learner_performance_data(student_id)
    return jsonify(performance_data)


def process_quiz_submission_direct(student_id, quiz_data, answers):
    """Process quiz submission directly without relying on quiz_engine"""
    try:
        # Create quiz record first
        quiz = Quiz(student_id=student_id,
                    topic_id=quiz_data['topic_id'],
                    question_set_id=quiz_data['question_set_id'],
                    total_marks=quiz_data['total_marks'])
        db.session.add(quiz)
        db.session.flush()  # To get the quiz_id

        total_score = 0
        correct_answers = 0
        total_questions = len(quiz_data['questions'])

        # Process each answer
        for question_data in quiz_data['questions']:
            question_id = question_data['question_id']
            question = Question.query.filter_by(
                question_id=question_id).first()

            selected_option = answers.get(f'question_{question_id}', '')
            is_correct = selected_option == question.correct_option

            print(
                f"Question {question_id}: Selected='{selected_option}', Correct='{question.correct_option}', Match={is_correct}"
            )

            if is_correct:
                total_score += question.marks_worth
                correct_answers += 1

            # Create quiz response record
            response = QuizResponse(
                quiz_id=quiz.quiz_id,
                question_id=question_id,
                selected_option=selected_option,
                is_correct=is_correct,
                time_taken=30  # Default time taken
            )
            db.session.add(response)

        # Update quiz record
        quiz.score = (total_score /
                      quiz.total_marks) * 100 if quiz.total_marks > 0 else 0
        quiz.date_taken = datetime.utcnow()

        db.session.commit()

        # Update performance trends
        quiz_engine._update_performance_trends(student_id, quiz.topic_id,
                                               quiz.score)

        # Prepare results
        results = {
            'quiz_id': quiz.quiz_id,
            'score': quiz.score,
            'total_marks': quiz.total_marks,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'percentage': round(quiz.score, 2),
            'passed': quiz.score >= 70,  # Default threshold
            'success_threshold': 70
        }

        return results

    except Exception as e:
        print(f"Error processing quiz submission: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

        # Return basic error result structure to prevent template errors
        return {
            'quiz_id': None,
            'score': 0,
            'total_marks': quiz_data.get('total_marks', 0),
            'correct_answers': 0,
            'total_questions': len(quiz_data.get('questions', [])),
            'percentage': 0,
            'passed': False,
            'success_threshold': 70,
            'error': str(e)
        }


def get_learner_performance_data(student_id):
    """Get comprehensive performance data for a learner"""
    # Get recent quizzes
    recent_quizzes = Quiz.query.filter_by(student_id=student_id).order_by(
        Quiz.date_taken.desc()).limit(10).all()

    # Get performance trends
    trends = PerformanceTrend.query.filter_by(student_id=student_id).all()

    # Calculate subject-wise proficiency, excluding hidden subjects
    hidden_subjects = HIDDEN_SUBJECTS
    subject_proficiency = {}
    for trend in trends:
        subject_name = trend.topic.subject.name
        if subject_name not in hidden_subjects:
            if subject_name not in subject_proficiency:
                subject_proficiency[subject_name] = []
            subject_proficiency[subject_name].append(trend.proficiency_score)

    # Average proficiency per subject
    for subject in subject_proficiency:
        scores = subject_proficiency[subject]
        subject_proficiency[subject] = sum(scores) / len(
            scores) if scores else 0

    return {
        'recent_quizzes': [{
            'topic': q.topic.name,
            'score': q.score,
            'date': q.date_taken.strftime('%Y-%m-%d')
        } for q in recent_quizzes],
        'subject_proficiency':
        subject_proficiency,
        'trends': [{
            'topic': t.topic.name,
            'score': t.proficiency_score,
            'data': t.trend_graph_data
        } for t in trends]
    }


def get_class_overview_data():
    """Get class overview data for educator dashboard"""
    # Get all learners
    learners = Student.query.all()

    # Calculate class statistics
    total_learners = len(learners)
    total_quizzes = Quiz.query.count()

    # Get subject-wise performance, excluding hidden subjects
    hidden_subjects = HIDDEN_SUBJECTS
    subjects = Subject.query.filter(~Subject.name.in_(hidden_subjects)).all()
    subject_stats = {}

    for subject in subjects:
        quizzes = Quiz.query.join(Topic).filter(
            Topic.subject_id == subject.subject_id).all()
        if quizzes:
            avg_score = sum(q.score for q in quizzes) / len(quizzes)
            subject_stats[subject.name] = {
                'average_score': round(avg_score, 2),
                'total_quizzes': len(quizzes)
            }

    return {
        'total_learners': total_learners,
        'total_quizzes': total_quizzes,
        'subject_stats': subject_stats
    }


def get_learners_traffic_light_data():
    """Get traffic light system data for learners"""
    learners = Student.query.all()
    traffic_light_data = []

    for learner in learners:
        # Calculate overall performance
        recent_quizzes = Quiz.query.filter_by(
            student_id=learner.student_id).order_by(
                Quiz.date_taken.desc()).limit(5).all()

        if recent_quizzes:
            avg_score = sum(q.score
                            for q in recent_quizzes) / len(recent_quizzes)

            # Determine traffic light status
            if avg_score >= 80:
                status = 'green'  # Strong
            elif avg_score >= 60:
                status = 'amber'  # Moderate
            else:
                status = 'red'  # Needs help
        else:
            status = 'gray'  # No data

        traffic_light_data.append({
            'learner_name':
            learner.user.full_name,
            'student_id':
            learner.student_id,
            'status':
            status,
            'avg_score':
            round(avg_score, 2) if recent_quizzes else 0
        })

    return traffic_light_data


def get_admin_analytics():
    """Get comprehensive analytics data for admin dashboard"""
    from datetime import datetime, timedelta
    from sqlalchemy import func, desc

    # System-wide Overview
    total_users = User.query.count()
    total_learners = User.query.filter_by(role='student').count()
    total_educators = User.query.filter_by(role='teacher').count()
    total_admins = User.query.filter_by(role='admin').count()

    # Active users (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    active_users_30d = Quiz.query.filter(
        Quiz.date_taken >= thirty_days_ago).distinct(Quiz.student_id).count()
    active_users_7d = Quiz.query.filter(
        Quiz.date_taken >= seven_days_ago).distinct(Quiz.student_id).count()

    # Course/Subject metrics
    total_subjects = Subject.query.count()
    total_topics = Topic.query.count()
    total_questions = Question.query.count()

    # Quiz and performance metrics
    total_quizzes = Quiz.query.count()
    total_quiz_responses = QuizResponse.query.count()

    # Calculate overall performance metrics
    avg_score = db.session.query(func.avg(Quiz.score)).scalar() or 0
    completion_rate = (Quiz.query.filter(Quiz.score >= 70).count() /
                       max(total_quizzes, 1)) * 100

    # Recent activity (last 7 days)
    recent_quizzes = Quiz.query.filter(
        Quiz.date_taken >= seven_days_ago).count()
    recent_users = Quiz.query.filter(
        Quiz.date_taken >= seven_days_ago).distinct(Quiz.student_id).count()

    # Top performing learners
    top_learners = db.session.query(
        Student.student_id,
        User.full_name,
        func.avg(Quiz.score).label('avg_score'),
        func.count(Quiz.id).label('quiz_count')
    ).join(User, Student.user_id == User.id)\
     .join(Quiz, Student.student_id == Quiz.student_id)\
     .group_by(Student.student_id, User.full_name)\
     .order_by(desc('avg_score'))\
     .limit(10).all()

    # Students needing help (low performance)
    struggling_learners = db.session.query(
        Student.student_id,
        User.full_name,
        func.avg(Quiz.score).label('avg_score'),
        func.count(Quiz.id).label('quiz_count')
    ).join(User, Student.user_id == User.id)\
     .join(Quiz, Student.student_id == Quiz.student_id)\
     .group_by(Student.student_id, User.full_name)\
     .having(func.avg(Quiz.score) < 60)\
     .order_by('avg_score')\
     .limit(10).all()

    # Subject performance analysis
    subject_performance = db.session.query(
        Subject.name,
        func.avg(Quiz.score).label('avg_score'),
        func.count(Quiz.id).label('quiz_count')
    ).join(Topic, Subject.subject_id == Topic.subject_id)\
     .join(Quiz, Topic.topic_id == Quiz.topic_id)\
     .group_by(Subject.name)\
     .order_by(desc('avg_score')).all()

    # Enrollment trends (quiz attempts per topic)
    popular_topics = db.session.query(
        Topic.name,
        Subject.name.label('subject_name'),
        func.count(Quiz.id).label('quiz_count')
    ).join(Subject, Topic.subject_id == Subject.subject_id)\
     .join(Quiz, Topic.topic_id == Quiz.topic_id)\
     .group_by(Topic.name, Subject.name)\
     .order_by(desc('quiz_count'))\
     .limit(10).all()

    # Daily activity for the last 7 days
    daily_activity = []
    for i in range(7):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        daily_quizzes = Quiz.query.filter(Quiz.date_taken >= day_start,
                                          Quiz.date_taken < day_end).count()

        daily_activity.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'quizzes': daily_quizzes
        })

    # Performance trends
    performance_trends = PerformanceTrend.query.order_by(
        PerformanceTrend.last_updated.desc()).limit(30).all()

    # Calculate growth metrics
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_users_today = User.query.filter(User.created_at >= yesterday).count()

    last_week = datetime.utcnow() - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= last_week).count()

    return {
        'system_overview': {
            'total_users': total_users,
            'total_learners': total_learners,
            'total_educators': total_educators,
            'total_admins': total_admins,
            'active_users_30d': active_users_30d,
            'active_users_7d': active_users_7d,
            'new_users_today': new_users_today,
            'new_users_week': new_users_week
        },
        'content_metrics': {
            'total_subjects': total_subjects,
            'total_topics': total_topics,
            'total_questions': total_questions,
            'total_quizzes': total_quizzes,
            'total_responses': total_quiz_responses
        },
        'performance_metrics': {
            'average_score': round(avg_score, 2),
            'completion_rate': round(completion_rate, 2),
            'recent_quizzes': recent_quizzes,
            'recent_active_users': recent_users
        },
        'top_performers': [{
            'name': learner.full_name,
            'avg_score': round(learner.avg_score, 2),
            'quiz_count': learner.quiz_count
        } for learner in top_learners],
        'struggling_learners': [{
            'name': learner.full_name,
            'avg_score': round(learner.avg_score, 2),
            'quiz_count': learner.quiz_count
        } for learner in struggling_learners],
        'subject_performance': [{
            'subject': subject.name,
            'avg_score': round(subject.avg_score, 2),
            'quiz_count': subject.quiz_count
        } for subject in subject_performance],
        'popular_topics': [{
            'topic': topic.name,
            'subject': topic.subject_name,
            'quiz_count': topic.quiz_count
        } for topic in popular_topics],
        'daily_activity':
        daily_activity[::-1],  # Reverse to show oldest first
        'performance_trends': [{
            'date': trend.last_updated.strftime('%Y-%m-%d'),
            'score': trend.proficiency_score
        } for trend in performance_trends]
    }


# Removed Adaptive Quiz Routes - No longer needed

# Removed adaptive quiz submission routes - No longer needed


@app.route('/api/predict_topics/<student_id>')
@login_required
def api_predict_topics(student_id):
    """API endpoint to get topic predictions for a learner"""
    try:
        # Ensure user can only access their own data or is a educator/admin
        if current_user.role == 'student':
            learner = Student.query.filter_by(user_id=current_user.id).first()
            if not learner or learner.student_id != student_id:
                return jsonify({'error': 'Unauthorized'}), 403
        elif current_user.role not in ['educator', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        # Get instant predictions using fast service
        predictions = fast_prediction_service.get_topic_predictions(student_id)
        return jsonify(predictions)

    except Exception as e:
        return jsonify({'error': 'Failed to get topic predictions'}), 500


@app.route('/api/performance_analysis/<student_id>')
@login_required
def api_performance_analysis(student_id):
    """API endpoint to get detailed performance analysis for a learner"""
    try:
        # Ensure user can only access their own data or is a educator/admin
        if current_user.role == 'student':
            learner = Student.query.filter_by(user_id=current_user.id).first()
            if not learner or learner.student_id != student_id:
                return jsonify({'error': 'Unauthorized'}), 403
        elif current_user.role not in ['educator', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        # Get fast performance analysis
        analysis = fast_prediction_service.get_performance_analysis(student_id)
        return jsonify(analysis)

    except Exception as e:
        return jsonify({'error': 'Failed to get performance analysis'}), 500


@app.route('/topic_predictions')
@login_required
def topic_predictions():
    """Page to display topic predictions for learners"""
    if current_user.role != 'student':
        return redirect(url_for('landing'))

    try:
        # Get learner data
        learner = Student.query.filter_by(user_id=current_user.id).first()
        if not learner:
            flash('Student profile not found', 'error')
            return redirect(url_for('learner_dashboard'))

        # Get instant topic predictions using fast service
        predictions = fast_prediction_service.get_topic_predictions(
            learner.student_id)

        # Get instant performance analysis using fast service
        analysis = fast_prediction_service.get_performance_analysis(
            learner.student_id)

        return render_template('topic_predictions.html',
                               predictions=predictions,
                               analysis=analysis,
                               learner=learner)

    except Exception as e:
        flash('Unable to load topic predictions', 'error')
        return redirect(url_for('learner_dashboard'))


@app.route('/api/ml_model_info')
@login_required
def api_ml_model_info():
    """API endpoint to get information about the ML model"""
    try:
        if current_user.role not in ['educator', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        info = {
            'model_trained': topic_prediction_service.is_trained,
            'model_type': 'Logistic Regression',
            'feature_count': len(topic_prediction_service.feature_columns),
            'features': topic_prediction_service.feature_columns,
            'target_classes': ['Addition', 'Subtraction', 'Multiplication'],
            'training_data_source': 'score_data.csv'
        }

        return jsonify(info)

    except Exception as e:
        return jsonify({'error': 'Failed to get model information'}), 500


@app.route('/subject_selection')
@login_required
def subject_selection():
    """Subject selection page for the new quiz flow"""
    if current_user.role != 'student':
        return redirect(url_for('landing'))

    try:
        # Get learner data
        learner = Student.query.filter_by(user_id=current_user.id).first()
        if not learner:
            flash('Student profile not found', 'error')
            return redirect(url_for('learner_dashboard'))

        # Get all subjects with their topics, excluding hidden subjects
        hidden_subjects = HIDDEN_SUBJECTS
        subjects = Subject.query.filter(
            ~Subject.name.in_(hidden_subjects)).all()

        # Calculate subject progress
        subject_progress = {}
        for subject in subjects:
            if subject.topics:
                total_topics = len(subject.topics)
                completed_topics = 0

                for topic in subject.topics:
                    # Check if learner has completed quizzes for this topic
                    quizzes = Quiz.query.filter_by(
                        student_id=learner.student_id,
                        topic_id=topic.topic_id).all()

                    if quizzes:
                        avg_score = sum(quiz.score
                                        for quiz in quizzes) / len(quizzes)
                        if avg_score >= 80:  # Consider 80% as completed
                            completed_topics += 1

                subject_progress[subject.subject_id] = round(
                    (completed_topics / total_topics) *
                    100, 1) if total_topics > 0 else 0

        return render_template('subject_selection.html',
                               subjects=subjects,
                               subject_progress=subject_progress)

    except Exception as e:
        flash('Unable to load subjects', 'error')
        return redirect(url_for('learner_dashboard'))


@app.route('/topic_selection/<subject_id>')
@login_required
def topic_selection(subject_id):
    """Topic selection page for a specific subject"""
    if current_user.role != 'student':
        return redirect(url_for('landing'))

    try:
        # Get learner data
        learner = Student.query.filter_by(user_id=current_user.id).first()
        if not learner:
            flash('Student profile not found', 'error')
            return redirect(url_for('learner_dashboard'))

        # Get subject and its topics
        subject = Subject.query.filter_by(subject_id=subject_id).first()
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('subject_selection'))

        topics = Topic.query.filter_by(subject_id=subject_id).all()

        # Calculate topic progress (simplified - no level tracking)
        topic_progress = {}
        for topic in topics:
            # Get all quizzes for this topic
            quizzes = Quiz.query.filter_by(student_id=learner.student_id,
                                           topic_id=topic.topic_id).all()

            if quizzes:
                # Calculate overall progress
                total_score = sum(quiz.score for quiz in quizzes)
                total_possible = sum(quiz.total_marks for quiz in quizzes)
                overall_progress = round((total_score / total_possible) *
                                         100, 1) if total_possible > 0 else 0

                topic_progress[topic.topic_id] = {
                    'overall':
                    overall_progress,
                    'attempts':
                    len(quizzes),
                    'best_score':
                    round(max(quiz.score
                              for quiz in quizzes), 1) if quizzes else 0
                }

        return render_template('topic_selection.html',
                               subject=subject,
                               topics=topics,
                               topic_progress=topic_progress)

    except Exception as e:
        # Log the specific error for debugging
        print(f"Error in topic_selection: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Unable to load topics', 'error')
        return redirect(url_for('subject_selection'))


@app.route('/learning_roadmap')
@login_required
def learning_roadmap():
    """Learning roadmap page with progress visualization"""
    if current_user.role != 'student':
        return redirect(url_for('landing'))

    try:
        # Get learner data
        learner = Student.query.filter_by(user_id=current_user.id).first()
        if not learner:
            flash('Student profile not found', 'error')
            return redirect(url_for('learner_dashboard'))

        # Get all subjects and calculate progress, excluding hidden subjects
        hidden_subjects = HIDDEN_SUBJECTS
        subjects = Subject.query.filter(
            ~Subject.name.in_(hidden_subjects)).all()
        roadmap_data = []

        total_progress = 0
        completed_topics = 0
        total_topics = 0

        for subject in subjects:
            if not subject.topics:
                continue

            subject_topics = []
            subject_completed = 0

            for topic in subject.topics:
                total_topics += 1

                # Get quizzes for this topic
                quizzes = Quiz.query.filter_by(student_id=learner.student_id,
                                               topic_id=topic.topic_id).all()

                # Determine topic status
                if quizzes:
                    avg_score = sum(quiz.score
                                    for quiz in quizzes) / len(quizzes)
                    total_possible = sum(quiz.total_marks for quiz in quizzes)
                    if total_possible > 0:
                        progress = round(
                            (sum(quiz.score
                                 for quiz in quizzes) / total_possible) * 100,
                            1)
                    else:
                        progress = 0

                    if avg_score >= 80:
                        status = 'completed'
                        subject_completed += 1
                        completed_topics += 1
                    elif avg_score >= 60:
                        status = 'current'
                    else:
                        status = 'unlocked'
                else:
                    progress = 0
                    status = 'unlocked'

                subject_topics.append({
                    'topic_id': topic.topic_id,
                    'name': topic.name,
                    'difficulty_level': topic.difficulty_level,
                    'status': status,
                    'progress': progress
                })

            # Calculate subject progress
            subject_progress = round(
                (subject_completed / len(subject.topics)) *
                100, 1) if subject.topics else 0
            total_progress += subject_progress

            # Determine subject icon
            if 'Math' in subject.name or 'Addition' in subject.name or 'Subtraction' in subject.name:
                icon = 'calculator'
            elif 'Science' in subject.name:
                icon = 'flask'
            elif 'English' in subject.name:
                icon = 'book'
            else:
                icon = 'bookmark'

            roadmap_data.append({
                'name': subject.name,
                'icon': icon,
                'progress': subject_progress,
                'topics': subject_topics
            })

        # Calculate overall progress
        overall_progress = round(total_progress /
                                 len(subjects), 1) if subjects else 0

        # Generate recommendations
        recommendations = [{
            'title': 'Complete Easy Topics',
            'description': 'Focus on easier topics to build confidence',
            'priority': 'High',
            'priority_color': 'success',
            'icon': 'leaf',
            'action_url': url_for('subject_selection'),
            'action_text': 'Start Quiz'
        }, {
            'title': 'Review Weak Areas',
            'description': 'Revisit topics where you scored below 70%',
            'priority': 'Medium',
            'priority_color': 'warning',
            'icon': 'redo',
            'action_url': url_for('ai_support'),
            'action_text': 'Get AI Help'
        }]

        # Generate achievement badges
        badges = [{
            'name':
            'First Steps',
            'description':
            'Complete your first quiz',
            'icon':
            'medal',
            'earned':
            completed_topics > 0,
            'earned_date':
            'Recently' if completed_topics > 0 else None,
            'progress':
            min(100, completed_topics * 100) if completed_topics > 0 else 0
        }, {
            'name': 'Topic Master',
            'description': 'Master 5 topics with 80%+ accuracy',
            'icon': 'crown',
            'earned': completed_topics >= 5,
            'earned_date': 'Recently' if completed_topics >= 5 else None,
            'progress': min(100, (completed_topics / 5) * 100)
        }]

        return render_template(
            'learning_roadmap.html',
            roadmap_data=roadmap_data,
            overall_progress=overall_progress,
            completed_topics=completed_topics,
            current_streak=7,  # Can be calculated from quiz dates
            next_goal='Complete 3 more topics',
            recommendations=recommendations,
            badges=badges)

    except Exception as e:
        flash('Unable to load learning roadmap', 'error')
        return redirect(url_for('learner_dashboard'))


@app.route('/ai_support')
@login_required
def ai_support():
    """AI Support page with reports, statistics, and predictions"""
    if current_user.role != 'student':
        return redirect(url_for('landing'))

    try:
        # Get learner data
        learner = Student.query.filter_by(user_id=current_user.id).first()
        if not learner:
            flash('Student profile not found', 'error')
            return redirect(url_for('learner_dashboard'))

        # Get AI feedback using fast service
        ai_report = fast_ai.generate_learner_feedback(learner.student_id)

        # Get statistics
        quizzes = Quiz.query.filter_by(student_id=learner.student_id).all()

        statistics = None
        if quizzes:
            # Calculate basic statistics
            total_score = sum(quiz.score for quiz in quizzes)
            total_possible = sum(quiz.total_marks for quiz in quizzes)
            overall_accuracy = round((total_score / total_possible) *
                                     100, 1) if total_possible > 0 else 0

            # Calculate average time per question
            total_time = sum(quiz.time_taken for quiz in quizzes
                             if quiz.time_taken)
            total_questions = len(quizzes)
            avg_time_per_question = round(total_time / total_questions,
                                          1) if total_questions > 0 else 0

            # Performance timeline (last 10 quizzes)
            recent_quizzes = sorted(quizzes, key=lambda x: x.date_taken)[-10:]
            timeline_labels = [
                f"Quiz {i+1}" for i in range(len(recent_quizzes))
            ]
            timeline_data = [
                round((quiz.score / quiz.total_marks) * 100, 1)
                for quiz in recent_quizzes
            ]

            # Topic accuracy
            topic_accuracy = {}
            for quiz in quizzes:
                topic_name = quiz.topic.name
                if topic_name not in topic_accuracy:
                    topic_accuracy[topic_name] = {'score': 0, 'total': 0}
                topic_accuracy[topic_name]['score'] += quiz.score
                topic_accuracy[topic_name]['total'] += quiz.total_marks

            topic_labels = list(topic_accuracy.keys())
            topic_data = [
                round((topic_accuracy[topic]['score'] /
                       topic_accuracy[topic]['total']) * 100, 1)
                for topic in topic_labels
            ]

            statistics = {
                'overall_accuracy': overall_accuracy,
                'avg_time_per_question': avg_time_per_question,
                'total_questions': total_questions,
                'correct_answers': round(total_score),
                'performance_timeline': {
                    'labels': timeline_labels,
                    'data': timeline_data
                },
                'topic_accuracy': {
                    'labels': topic_labels,
                    'data': topic_data
                },
                'strength_weakness': {
                    'labels': topic_labels,
                    'data': topic_data
                }
            }

        return render_template('ai_support.html',
                               ai_report=ai_report,
                               statistics=statistics)

    except Exception as e:
        flash('Unable to load AI support', 'error')
        return redirect(url_for('learner_dashboard'))


@app.route('/quiz_history')
@login_required
def quiz_history():
    """Quiz history page"""
    if current_user.role != 'student':
        return redirect(url_for('landing'))

    try:
        # Get learner data
        learner = Student.query.filter_by(user_id=current_user.id).first()
        if not learner:
            flash('Student profile not found', 'error')
            return redirect(url_for('learner_dashboard'))

        # Get quiz history
        quizzes = Quiz.query.filter_by(student_id=learner.student_id).order_by(
            Quiz.date_taken.desc()).all()

        return render_template('quiz_history.html', quizzes=quizzes)

    except Exception as e:
        flash('Unable to load quiz history', 'error')
        return redirect(url_for('learner_dashboard'))


@app.route('/api/quiz_details/<quiz_id>')
@login_required
def api_quiz_details(quiz_id):
    """API endpoint to get detailed quiz information"""
    try:
        # Get learner data
        learner = Student.query.filter_by(user_id=current_user.id).first()
        if not learner:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404

        # Get quiz
        quiz = Quiz.query.filter_by(quiz_id=quiz_id,
                                    student_id=learner.student_id).first()
        if not quiz:
            return jsonify({'success': False, 'error': 'Quiz not found'}), 404

        # Get quiz responses
        responses = QuizResponse.query.filter_by(quiz_id=quiz_id).all()

        quiz_data = {
            'subject':
            quiz.topic.subject.name,
            'topic':
            quiz.topic.name,
            'difficulty':
            quiz.question_set.difficulty_level,
            'score':
            quiz.score,
            'total_marks':
            quiz.total_marks,
            'percentage':
            round((quiz.score / quiz.total_marks) * 100, 1),
            'date':
            quiz.date_taken.strftime('%Y-%m-%d %H:%M'),
            'time_taken':
            f"{quiz.time_taken // 60}m {quiz.time_taken % 60}s"
            if quiz.time_taken else 'N/A'
        }

        response_data = []
        for response in responses:
            response_data.append({
                'selected_option': response.selected_option,
                'correct_option': response.question.correct_option,
                'is_correct': response.is_correct
            })

        return jsonify({
            'success': True,
            'quiz': quiz_data,
            'responses': response_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to load quiz details'
        }), 500


# Configuration for file uploads
UPLOAD_FOLDER = 'static/images/quiz/educator_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, prefix=""):
    """Save uploaded file and return the relative path"""
    if not file or not allowed_file(file.filename):
        return None

    # Create unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{prefix}_{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Ensure directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Save file
    file.save(filepath)

    # Return relative path for web access
    return f"/static/images/quiz/educator_uploads/{unique_filename}"


@app.route('/api/create-content', methods=['POST'])
@login_required
def create_content():
    """API endpoint to create new educational content"""
    if current_user.role != 'teacher':
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        # Get form data
        subject_name = request.form.get(
            'topicName')  # This is actually the subject name dont forget
        subject_description = request.form.get('topicDescription', '')
        subtopics_json = request.form.get('subTopics')

        if not subject_name or not subtopics_json:
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        subtopics_data = json.loads(subtopics_json)

        # Create or get subject
        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            subject = Subject(name=subject_name,
                              description=subject_description)
            db.session.add(subject)
            db.session.flush()

        # Process each sub-topic (these are the actual topics)
        for subtopic_index, subtopic_data in enumerate(subtopics_data):
            if not subtopic_data.get('name') or not subtopic_data.get(
                    'questions'):
                continue

            # Create topic for this sub-topic
            topic = Topic(subject_id=subject.subject_id,
                          name=subtopic_data['name'],
                          difficulty_level=subtopic_data.get(
                              'difficulty', 'medium'))
            db.session.add(topic)
            db.session.flush()

            # Create question set for this topic
            question_set = QuestionSet(
                topic_id=topic.topic_id,
                subject_id=subject.subject_id,
                difficulty_level=subtopic_data.get('difficulty', 'medium'),
                min_questions=len(subtopic_data['questions']),
                max_questions=len(subtopic_data['questions']),
                success_threshold=80.0)
            db.session.add(question_set)
            db.session.flush()

            question_ids = []

            # Process each question
            for question_index, question_data in enumerate(
                    subtopic_data['questions']):
                if not question_data.get('text'):
                    continue

                # Handle image upload if present
                image_url = None
                if question_data.get('hasImage') and question_data.get(
                        'imageKey'):
                    image_file = request.files.get(question_data['imageKey'])
                    if image_file:
                        image_url = save_uploaded_file(
                            image_file,
                            f"{subject_name}_{subtopic_data['name']}_q{question_index}"
                        )

                # Create question
                question = Question(
                    set_id=question_set.question_set_id,
                    description=question_data['text'],
                    options=[
                        question_data['optionA'], question_data['optionB'],
                        question_data['optionC'], question_data['optionD']
                    ],
                    correct_option=question_data['correctAnswer'],
                    explanation=question_data.get('explanation', ''),
                    image_url=image_url,
                    marks_worth=1)
                db.session.add(question)
                db.session.flush()

                question_ids.append(question.question_id)

            # Update question set with question IDs
            question_set.question_ids = question_ids
            question_set.total_marks = len(question_ids)

        # Commit all changes
        db.session.commit()

        return jsonify({
            'success': True,
            'message':
            f'Content created successfully! Subject "{subject_name}" with {len(subtopics_data)} topics.',
            'subject_id': subject.subject_id
        })

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating content: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error creating content: {str(e)}'
        }), 500


@app.route('/api/content-library')
@login_required
def content_library():
    """API endpoint to get educator's content library"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get all subjects with their topic and question counts
        subjects_data = []
        subjects = Subject.query.all()

        for subject in subjects:
            # Count topics
            topics_count = Topic.query.filter_by(
                subject_id=subject.subject_id).count()

            # Count total questions
            questions_count = db.session.query(Question).join(
                QuestionSet).join(Topic).filter(
                    Topic.subject_id == subject.subject_id).count()

            subjects_data.append({
                'id': subject.subject_id,
                'name': subject.name,
                'topics_count': topics_count,
                'questions_count': questions_count,
                'created_at':
                subject.id  # Using id as a proxy for creation order
            })

        return jsonify({'success': True, 'subjects': subjects_data})

    except Exception as e:
        app.logger.error(f"Error loading content library: {str(e)}")
        return jsonify({'error':
                        f'Error loading content library: {str(e)}'}), 500


@app.route('/api/manage-content')
@login_required
def manage_content():
    """API endpoint to get all subjects, topics, and questions in nested structure"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403

    try:
        subjects_data = []
        subjects = Subject.query.all()

        for subject in subjects:
            # Get all topics for this subject
            topics = Topic.query.filter_by(subject_id=subject.subject_id).all()
            topics_data = []

            for topic in topics:
                # Get question set for this topic
                question_set = QuestionSet.query.filter_by(topic_id=topic.topic_id).first()
                questions_data = []

                if question_set and question_set.question_ids:
                    # Get all questions for this topic
                    questions = Question.query.filter(Question.question_id.in_(question_set.question_ids)).all()
                    for question in questions:
                        # Parse options from JSON array
                        options = question.options or []
                        questions_data.append({
                            'id': question.question_id,
                            'description': question.description,  # Use description field
                            'options': options,  # Use options array
                            'correct_option': question.correct_option,
                            'marks_worth': question.marks_worth,
                            'explanation': question.explanation,
                            'image_url': question.image_url
                        })

                topics_data.append({
                    'id': topic.topic_id,
                    'name': topic.name,
                    'difficulty_level': topic.difficulty_level,  # Use difficulty_level instead of description
                    'questions': questions_data
                })

            subjects_data.append({
                'id': subject.subject_id,
                'name': subject.name,
                'description': subject.description,
                'topics': topics_data
            })

        return jsonify({'subjects': subjects_data})

    except Exception as e:
        app.logger.error(f"Error loading manage content: {str(e)}")
        return jsonify({'error': f'Error loading content: {str(e)}'}), 500


@app.route('/api/subject/<int:subject_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_subject(subject_id):
    """Edit or delete a subject"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403

    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'PUT':
        try:
            data = request.get_json()
            subject.name = data.get('name', subject.name)
            subject.description = data.get('description', subject.description)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Subject updated successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating subject: {str(e)}")
            return jsonify({'error': f'Error updating subject: {str(e)}'}), 500

    elif request.method == 'DELETE':
        try:
            # Delete all associated topics and questions
            topics = Topic.query.filter_by(subject_id=subject_id).all()
            for topic in topics:
                question_set = QuestionSet.query.filter_by(topic_id=topic.topic_id).first()
                if question_set and question_set.question_ids:
                    Question.query.filter(Question.question_id.in_(question_set.question_ids)).delete(synchronize_session=False)
                    db.session.delete(question_set)
                db.session.delete(topic)
            
            db.session.delete(subject)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Subject deleted successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting subject: {str(e)}")
            return jsonify({'error': f'Error deleting subject: {str(e)}'}), 500


@app.route('/api/topic/<int:topic_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_topic(topic_id):
    """Edit or delete a topic"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403

    topic = Topic.query.get_or_404(topic_id)

    if request.method == 'PUT':
        try:
            data = request.get_json()
            topic.name = data.get('name', topic.name)
            topic.difficulty_level = data.get('difficulty_level', topic.difficulty_level)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Topic updated successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating topic: {str(e)}")
            return jsonify({'error': f'Error updating topic: {str(e)}'}), 500

    elif request.method == 'DELETE':
        try:
            # Delete all associated questions
            question_set = QuestionSet.query.filter_by(topic_id=topic_id).first()
            if question_set and question_set.question_ids:
                Question.query.filter(Question.question_id.in_(question_set.question_ids)).delete(synchronize_session=False)
                db.session.delete(question_set)
            
            db.session.delete(topic)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Topic deleted successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting topic: {str(e)}")
            return jsonify({'error': f'Error deleting topic: {str(e)}'}), 500


@app.route('/api/question/<int:question_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_question(question_id):
    """Edit or delete a question"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403

    question = Question.query.get_or_404(question_id)

    if request.method == 'PUT':
        try:
            data = request.get_json()
            question.description = data.get('description', question.description)
            question.options = data.get('options', question.options)
            question.correct_option = data.get('correct_option', question.correct_option)
            question.marks_worth = data.get('marks_worth', question.marks_worth)
            question.explanation = data.get('explanation', question.explanation)
            question.image_url = data.get('image_url', question.image_url)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Question updated successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating question: {str(e)}")
            return jsonify({'error': f'Error updating question: {str(e)}'}), 500

    elif request.method == 'DELETE':
        try:
            # Remove question from question set
            question_sets = QuestionSet.query.all()
            for qs in question_sets:
                if qs.question_ids and question_id in qs.question_ids:
                    qs.question_ids.remove(question_id)
                    qs.total_marks = len(qs.question_ids)
            
            db.session.delete(question)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Question deleted successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting question: {str(e)}")
            return jsonify({'error': f'Error deleting question: {str(e)}'}), 500
