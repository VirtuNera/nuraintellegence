"""
Database optimization utilities for improved query performance
"""

from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from .models import Quiz, Student, User, Subject, Topic, PerformanceTrend


class DatabaseOptimizer:
    """Optimized database queries to reduce load and improve performance"""
    
    @staticmethod
    def get_dashboard_metrics_optimized():
        """Get dashboard metrics with optimized single queries"""
        from app import db
        
        # Get metrics in single queries to reduce database round trips
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # Total active learners this week (single query)
        recent_learners_count = db.session.query(Quiz.student_id).filter(
            Quiz.date_taken >= seven_days_ago
        ).distinct().count()
        
        # Top performing learners (single optimized query)
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
        
        # Struggling learners (single optimized query)
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
        
        # Subject performance (single optimized query)
        subject_performance = db.session.query(
            Subject.name,
            func.avg(Quiz.score).label('avg_score'),
            func.count(Quiz.id).label('quiz_count')
        ).join(Topic, Subject.subject_id == Topic.subject_id)\
         .join(Quiz, Topic.topic_id == Quiz.topic_id)\
         .group_by(Subject.name)\
         .order_by(desc('avg_score')).all()
        
        # Popular topics (single optimized query)
        popular_topics = db.session.query(
            Topic.name,
            func.count(Quiz.id).label('attempt_count'),
            func.avg(Quiz.score).label('avg_score')
        ).join(Quiz, Topic.topic_id == Quiz.topic_id)\
         .filter(Quiz.date_taken >= seven_days_ago)\
         .group_by(Topic.name)\
         .order_by(desc('attempt_count'))\
         .limit(10).all()
        
        return {
            'recent_learners_count': recent_learners_count,
            'top_learners': top_learners,
            'struggling_learners': struggling_learners,
            'subject_performance': subject_performance,
            'popular_topics': popular_topics
        }
    
    @staticmethod
    def get_student_performance_optimized(student_id):
        """Get student performance data with optimized queries"""
        from app import db
        
        # Recent quizzes with topic names (single JOIN query)
        recent_quizzes = db.session.query(
            Quiz.quiz_id,
            Quiz.score,
            Quiz.date_taken,
            Topic.name.label('topic_name'),
            Subject.name.label('subject_name')
        ).join(Topic, Quiz.topic_id == Topic.topic_id)\
         .join(Subject, Topic.subject_id == Subject.subject_id)\
         .filter(Quiz.student_id == student_id)\
         .order_by(desc(Quiz.date_taken))\
         .limit(10).all()
        
        # Performance trends (single query)
        performance_trends = PerformanceTrend.query.filter_by(
            student_id=student_id
        ).all()
        
        # Subject-wise performance (aggregated query)
        subject_performance = db.session.query(
            Subject.name,
            func.avg(Quiz.score).label('avg_score'),
            func.count(Quiz.id).label('quiz_count'),
            func.max(Quiz.date_taken).label('last_attempt')
        ).join(Topic, Subject.subject_id == Topic.subject_id)\
         .join(Quiz, Topic.topic_id == Quiz.topic_id)\
         .filter(Quiz.student_id == student_id)\
         .group_by(Subject.name)\
         .order_by(desc('avg_score')).all()
        
        return {
            'recent_quizzes': recent_quizzes,
            'performance_trends': performance_trends,
            'subject_performance': subject_performance
        }
    
    @staticmethod
    def get_available_subjects_cached():
        """Get available subjects with caching considerations"""
        from app import db
        
        # Hidden subjects to exclude
        HIDDEN_SUBJECTS = [
            'Mathematics', 'Science', 'English', 'History', 'Geography', 
            'PISA Mathematics', 'Question Set', 'Performance Log'
        ]
        
        # Get subjects with topic counts in single query
        subjects_with_topics = db.session.query(
            Subject.subject_id,
            Subject.name,
            Subject.description,
            func.count(Topic.topic_id).label('topic_count')
        ).outerjoin(Topic, Subject.subject_id == Topic.subject_id)\
         .filter(~Subject.name.in_(HIDDEN_SUBJECTS))\
         .group_by(Subject.subject_id, Subject.name, Subject.description)\
         .having(func.count(Topic.topic_id) > 0)\
         .order_by(Subject.name).all()
        
        return subjects_with_topics
    
    @staticmethod
    def batch_create_quiz_responses(responses_data):
        """Batch create quiz responses for better performance"""
        from app import db
        from .models import QuizResponse
        
        responses = [
            QuizResponse(**response_data) 
            for response_data in responses_data
        ]
        
        db.session.add_all(responses)
        db.session.commit()
        
        return len(responses)
    
    @staticmethod
    def cleanup_old_sessions(days_old=7):
        """Clean up old adaptive quiz sessions"""
        from app import db
        from .models import AdaptiveQuizSession
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted_count = db.session.query(AdaptiveQuizSession).filter(
            AdaptiveQuizSession.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        return deleted_count