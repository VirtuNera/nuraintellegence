"""
Database initialization script with sample data
"""
from app import app, db
from models import User, Student, Teacher, Admin, Subject, Topic, QuestionSet, Question
from werkzeug.security import generate_password_hash
import json

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create sample subjects
        subjects_data = [
            {"name": "Mathematics", "description": "Core mathematical concepts and problem solving"},
            {"name": "Science", "description": "Physics, Chemistry, and Biology fundamentals"},
            {"name": "English", "description": "Language arts, literature, and communication"},
            {"name": "History", "description": "World history and social studies"},
            {"name": "Geography", "description": "Physical and human geography"}
        ]
        
        subjects = []
        for subject_data in subjects_data:
            if not Subject.query.filter_by(name=subject_data["name"]).first():
                subject = Subject(**subject_data)
                db.session.add(subject)
                subjects.append(subject)
        
        db.session.commit()
        
        # Create sample topics
        topics_data = [
            {"subject_name": "Mathematics", "name": "Algebra Basics", "difficulty_level": "easy"},
            {"subject_name": "Mathematics", "name": "Quadratic Equations", "difficulty_level": "medium"},
            {"subject_name": "Mathematics", "name": "Calculus Fundamentals", "difficulty_level": "hard"},
            {"subject_name": "Science", "name": "Basic Chemistry", "difficulty_level": "easy"},
            {"subject_name": "Science", "name": "Physics Mechanics", "difficulty_level": "medium"},
            {"subject_name": "Science", "name": "Organic Chemistry", "difficulty_level": "hard"},
            {"subject_name": "English", "name": "Grammar Fundamentals", "difficulty_level": "easy"},
            {"subject_name": "English", "name": "Reading Comprehension", "difficulty_level": "medium"},
            {"subject_name": "English", "name": "Literary Analysis", "difficulty_level": "hard"},
        ]
        
        topics = []
        for topic_data in topics_data:
            subject = Subject.query.filter_by(name=topic_data["subject_name"]).first()
            if subject and not Topic.query.filter_by(name=topic_data["name"]).first():
                topic = Topic(
                    subject_id=subject.subject_id,
                    name=topic_data["name"],
                    difficulty_level=topic_data["difficulty_level"]
                )
                db.session.add(topic)
                topics.append(topic)
        
        db.session.commit()
        
        # Create sample question sets
        for topic in Topic.query.all():
            if not QuestionSet.query.filter_by(topic_id=topic.topic_id).first():
                question_set = QuestionSet(
                    topic_id=topic.topic_id,
                    subject_id=topic.subject_id,
                    difficulty_level=topic.difficulty_level,
                    min_questions=5,
                    max_questions=10,
                    success_threshold=70.0,
                    total_marks=10
                )
                db.session.add(question_set)
        
        db.session.commit()
        
        # Create sample questions
        sample_questions = [
            {
                "topic_name": "Algebra Basics",
                "questions": [
                    {
                        "description": "What is the value of x in the equation 2x + 5 = 11?",
                        "options": ["A) 2", "B) 3", "C) 4", "D) 5"],
                        "correct_option": "B",
                        "explanation": "2x + 5 = 11, so 2x = 6, therefore x = 3"
                    },
                    {
                        "description": "Simplify: 3x + 2x - x",
                        "options": ["A) 4x", "B) 5x", "C) 6x", "D) 3x"],
                        "correct_option": "A",
                        "explanation": "3x + 2x - x = 5x - x = 4x"
                    }
                ]
            },
            {
                "topic_name": "Basic Chemistry",
                "questions": [
                    {
                        "description": "What is the chemical symbol for water?",
                        "options": ["A) H2O", "B) CO2", "C) NaCl", "D) O2"],
                        "correct_option": "A",
                        "explanation": "Water is composed of two hydrogen atoms and one oxygen atom"
                    },
                    {
                        "description": "How many electrons does a neutral carbon atom have?",
                        "options": ["A) 4", "B) 6", "C) 8", "D) 12"],
                        "correct_option": "B",
                        "explanation": "Carbon has 6 protons, so a neutral atom has 6 electrons"
                    }
                ]
            }
        ]
        
        for question_data in sample_questions:
            topic = Topic.query.filter_by(name=question_data["topic_name"]).first()
            if topic:
                question_set = QuestionSet.query.filter_by(topic_id=topic.topic_id).first()
                if question_set:
                    for q in question_data["questions"]:
                        if not Question.query.filter_by(description=q["description"]).first():
                            question = Question(
                                set_id=question_set.question_set_id,
                                description=q["description"],
                                options=q["options"],
                                correct_option=q["correct_option"],
                                marks_worth=1,
                                explanation=q["explanation"]
                            )
                            db.session.add(question)
        
        db.session.commit()
        
        # Create sample admin user
        if not User.query.filter_by(email="admin@nuraai.com").first():
            admin_user = User(
                full_name="Nura AI Administrator",
                email="admin@nuraai.com",
                password_hash=generate_password_hash("admin123"),
                role="admin"
            )
            db.session.add(admin_user)
            db.session.commit()
            
            admin_profile = Admin(
                user_id=admin_user.id,
                department="System Administration",
                permissions=["full_access", "user_management", "system_monitoring", "data_export"]
            )
            db.session.add(admin_profile)
            db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()
