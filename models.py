from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('student', 'teacher', 'admin', name='user_roles'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False)
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False)
    admin_profile = db.relationship('Admin', backref='user', uselist=False)

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    grade_level = db.Column(db.String(20), nullable=True)
    preferred_subjects = db.Column(JSON)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='student', lazy=True)
    performance_trends = db.relationship('PerformanceTrend', backref='student', lazy=True)

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    school_name = db.Column(db.String(200))
    subjects_taught = db.Column(JSON)

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department = db.Column(db.String(100))
    permissions = db.Column(JSON)  # Store admin permissions as JSON
    last_login = db.Column(db.DateTime)

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    topics = db.relationship('Topic', backref='subject', lazy=True)

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    subject_id = db.Column(db.String(36), db.ForeignKey('subjects.subject_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)
    
    # Relationships
    question_sets = db.relationship('QuestionSet', backref='topic', lazy=True)

class QuestionSet(db.Model):
    __tablename__ = 'question_sets'
    
    id = db.Column(db.Integer, primary_key=True)
    question_set_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    topic_id = db.Column(db.String(36), db.ForeignKey('topics.topic_id'), nullable=False)
    subject_id = db.Column(db.String(36), db.ForeignKey('subjects.subject_id'))
    difficulty_level = db.Column(db.String(20), nullable=False)  # Very Easy, Easy, Medium, Hard, Very Hard
    question_ids = db.Column(JSON)  # Array of question IDs
    min_questions = db.Column(db.Integer, default=5)
    max_questions = db.Column(db.Integer, default=10)
    success_threshold = db.Column(db.Float, default=80.0)  # Percentage to advance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_marks = db.Column(db.Integer, default=0)
    
    # Relationships
    questions = db.relationship('Question', backref='question_set', lazy=True)

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    set_id = db.Column(db.String(36), db.ForeignKey('question_sets.question_set_id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    options = db.Column(JSON)  # Array of options
    correct_option = db.Column(db.String(10), nullable=False)
    marks_worth = db.Column(db.Integer, default=1)
    explanation = db.Column(db.Text)

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.student_id'), nullable=False)
    topic_id = db.Column(db.String(36), db.ForeignKey('topics.topic_id'), nullable=False)
    question_set_id = db.Column(db.String(36), db.ForeignKey('question_sets.question_set_id'), nullable=False)
    score = db.Column(db.Float, default=0.0)
    total_marks = db.Column(db.Integer, default=0)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)
    time_taken = db.Column(db.Integer)  # in seconds
    
    # Relationships
    responses = db.relationship('QuizResponse', backref='quiz', lazy=True)
    topic = db.relationship('Topic', backref='quizzes')
    question_set = db.relationship('QuestionSet', backref='quizzes')

class QuizResponse(db.Model):
    __tablename__ = 'quiz_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.quiz_id'), nullable=False)
    question_id = db.Column(db.String(36), db.ForeignKey('questions.question_id'), nullable=False)
    selected_option = db.Column(db.String(10))
    is_correct = db.Column(db.Boolean, default=False)
    time_taken = db.Column(db.Integer)  # in seconds
    nura_feedback = db.Column(db.Text)
    
    # Relationships
    question = db.relationship('Question', backref='responses')

class PerformanceTrend(db.Model):
    __tablename__ = 'performance_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    trend_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.student_id'), nullable=False)
    topic_id = db.Column(db.String(36), db.ForeignKey('topics.topic_id'), nullable=False)
    proficiency_score = db.Column(db.Float, default=0.0)
    trend_graph_data = db.Column(JSON)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    topic = db.relationship('Topic', backref='performance_trends')

class AdaptiveQuizSession(db.Model):
    __tablename__ = 'adaptive_quiz_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.student_id'), nullable=False)
    topic_id = db.Column(db.String(36), db.ForeignKey('topics.topic_id'), nullable=False)
    initial_difficulty = db.Column(db.String(20), nullable=False)  # Student's chosen starting difficulty
    current_difficulty = db.Column(db.String(20), nullable=False)  # Current difficulty level
    total_sets = db.Column(db.Integer, default=5)  # Number of question sets to complete
    current_set = db.Column(db.Integer, default=1)  # Current set number
    session_data = db.Column(JSON)  # Store per-set results and performance metrics
    final_proficiency_score = db.Column(db.Float, default=0.0)
    is_completed = db.Column(db.Boolean, default=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    
    # Relationships
    student = db.relationship('Student', backref='adaptive_quiz_sessions')
    topic = db.relationship('Topic', backref='adaptive_quiz_sessions')
