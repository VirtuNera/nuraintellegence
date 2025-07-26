"""
Unified Quiz Engine - Consolidates both regular and adaptive quiz functionality
with optimized performance and caching.
"""

import json
import random
from datetime import datetime, timedelta
from functools import lru_cache
from app import db
from .models import (
    Quiz, QuizResponse, Question, QuestionSet, Topic, Student, 
    PerformanceTrend, AdaptiveQuizSession
)
from .ai_service import NuraAI

class UnifiedQuizEngine:
    """
    Unified quiz engine that handles both regular quizzes and adaptive learning.
    Features performance optimizations and caching for better scalability.
    """
    
    DIFFICULTY_LEVELS = ['Very Easy', 'Easy', 'Medium', 'Hard', 'Very Hard']
    DIFFICULTY_PROGRESSION = {
        'Very Easy': {'up': 'Easy', 'down': None},
        'Easy': {'up': 'Medium', 'down': 'Very Easy'},
        'Medium': {'up': 'Hard', 'down': 'Easy'},
        'Hard': {'up': 'Very Hard', 'down': 'Medium'},
        'Very Hard': {'up': None, 'down': 'Hard'}
    }
    
    def __init__(self):
        self.nura_ai = NuraAI()
        self._question_cache = {}
    
    # Regular Quiz Methods
    def generate_quiz(self, student_id, topic_id, difficulty_level=None):
        """Generate a regular quiz with optional difficulty specification"""
        try:
            student = Student.query.filter_by(student_id=student_id).first()
            topic = Topic.query.filter_by(topic_id=topic_id).first()
            
            if not student or not topic:
                return None
            
            # Determine difficulty if not specified
            if not difficulty_level:
                difficulty_level = self._get_adaptive_difficulty(student_id, topic_id)
            
            # Get cached question set or fetch from database
            question_set = self._get_question_set(topic_id, difficulty_level)
            if not question_set:
                return None
            
            # Get questions with caching
            questions = self._get_questions_for_set(question_set.question_set_id)
            if not questions:
                return None
            
            # Select questions based on constraints
            selected_questions = self._select_questions(questions, question_set)
            
            # Create quiz record
            quiz = Quiz(
                student_id=student_id,
                topic_id=topic_id,
                question_set_id=question_set.question_set_id,
                total_marks=sum(q.marks_worth for q in selected_questions)
            )
            db.session.add(quiz)
            db.session.commit()
            
            return self._prepare_quiz_data(quiz, topic, difficulty_level, selected_questions, question_set)
            
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return None
    
    # Adaptive Quiz Methods
    def start_adaptive_session(self, student_id, topic_id, initial_difficulty, total_sets=5):
        """Start a new adaptive quiz session"""
        try:
            if initial_difficulty not in self.DIFFICULTY_LEVELS:
                raise ValueError(f"Invalid difficulty level: {initial_difficulty}")
            
            student = Student.query.filter_by(student_id=student_id).first()
            topic = Topic.query.filter_by(topic_id=topic_id).first()
            
            if not student or not topic:
                return None
            
            # Create adaptive session
            session = AdaptiveQuizSession(
                student_id=student_id,
                topic_id=topic_id,
                initial_difficulty=initial_difficulty,
                current_difficulty=initial_difficulty,
                total_sets=total_sets,
                current_set=1,
                session_data=json.dumps({
                    'sets_completed': [],
                    'performance_history': [],
                    'difficulty_adjustments': []
                })
            )
            
            db.session.add(session)
            db.session.commit()
            
            # Generate first question set
            first_set = self._generate_adaptive_set(
                session.session_id, topic_id, initial_difficulty, 1
            )
            
            if not first_set:
                return None
            
            return {
                'success': True,
                'session_id': session.session_id,
                'topic_name': topic.name,
                'initial_difficulty': initial_difficulty,
                'current_difficulty': initial_difficulty,
                'current_set': first_set,
                'current_set_number': 1,
                'total_sets': total_sets
            }
            
        except Exception as e:
            print(f"Error starting adaptive session: {e}")
            return None
    
    def process_adaptive_submission(self, session_id, quiz_data, answers, completion_time):
        """Process adaptive quiz submission and determine next difficulty"""
        try:
            session = AdaptiveQuizSession.query.filter_by(session_id=session_id).first()
            if not session:
                return None
            
            # Process the quiz using unified submission logic
            quiz_result = self.process_quiz_submission(
                session.student_id, quiz_data, answers, completion_time
            )
            
            if not quiz_result:
                return None
            
            # Calculate adaptive metrics
            correctness_percentage = quiz_result['percentage']
            average_time_per_question = completion_time / quiz_result['total_questions']
            is_fast_completion = average_time_per_question < 20
            
            # Update session data
            session_data = json.loads(session.session_data)
            
            set_result = {
                'set_number': session.current_set,
                'difficulty_level': session.current_difficulty,
                'quiz_id': quiz_result['quiz_id'],
                'score': quiz_result['score'],
                'correctness_percentage': correctness_percentage,
                'completion_time': completion_time,
                'average_time_per_question': average_time_per_question,
                'is_fast_completion': is_fast_completion,
                'total_questions': quiz_result['total_questions'],
                'correct_answers': quiz_result['correct_answers']
            }
            
            session_data['sets_completed'].append(set_result)
            session_data['performance_history'].append({
                'set_number': session.current_set,
                'score': quiz_result['score'],
                'time': completion_time
            })
            
            # Determine next difficulty
            next_difficulty = self._calculate_next_difficulty(
                session.current_difficulty, correctness_percentage, is_fast_completion
            )
            
            # Record difficulty adjustment
            if next_difficulty != session.current_difficulty:
                session_data['difficulty_adjustments'].append({
                    'from_set': session.current_set,
                    'from_difficulty': session.current_difficulty,
                    'to_difficulty': next_difficulty,
                    'reason': f"Performance: {correctness_percentage:.1f}%, Fast: {is_fast_completion}"
                })
            
            session.current_difficulty = next_difficulty
            session.current_set += 1
            session.session_data = json.dumps(session_data)
            
            db.session.commit()
            
            # Check if session is complete
            is_complete = session.current_set > session.total_sets
            
            result = {
                'set_results': set_result,
                'session_progress': {
                    'current_set': session.current_set - 1,
                    'total_sets': session.total_sets,
                    'is_complete': is_complete,
                    'next_difficulty': next_difficulty
                },
                'performance_summary': self._calculate_session_summary(session_data)
            }
            
            if not is_complete:
                # Generate next set
                next_set = self._generate_adaptive_set(
                    session_id, session.topic_id, next_difficulty, session.current_set
                )
                result['next_set'] = next_set
            
            return result
            
        except Exception as e:
            print(f"Error processing adaptive submission: {e}")
            return None
    
    def process_quiz_submission(self, student_id, quiz_data, answers, completion_time=None):
        """Unified quiz submission processing for both regular and adaptive quizzes"""
        try:
            quiz = Quiz.query.filter_by(quiz_id=quiz_data['quiz_id']).first()
            if not quiz:
                return None
            
            total_score = 0
            correct_answers = 0
            total_questions = len(quiz_data['questions'])
            
            # Batch process answers for better performance
            responses = []
            for question_data in quiz_data['questions']:
                question_id = question_data['question_id']
                question = Question.query.filter_by(question_id=question_id).first()
                
                selected_option = answers.get(f'question_{question_id}', '')
                is_correct = selected_option == question.correct_option
                
                if is_correct:
                    total_score += question.marks_worth
                    correct_answers += 1
                
                responses.append(QuizResponse(
                    quiz_id=quiz.quiz_id,
                    question_id=question_id,
                    selected_option=selected_option,
                    is_correct=is_correct,
                    time_taken=completion_time // total_questions if completion_time else 30
                ))
            
            # Batch insert responses
            db.session.add_all(responses)
            
            # Update quiz record
            quiz.score = (total_score / quiz.total_marks) * 100 if quiz.total_marks > 0 else 0
            quiz.date_taken = datetime.utcnow()
            if completion_time:
                quiz.time_taken = completion_time
            
            db.session.commit()
            
            # Update performance trends asynchronously
            self._update_performance_trends(student_id, quiz.topic_id, quiz.score)
            
            return {
                'quiz_id': quiz.quiz_id,
                'score': quiz.score,
                'total_marks': quiz.total_marks,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'percentage': round(quiz.score, 2),
                'passed': quiz.score >= quiz_data.get('success_threshold', 60),
                'success_threshold': quiz_data.get('success_threshold', 60)
            }
            
        except Exception as e:
            print(f"Error processing quiz submission: {e}")
            return None
    
    # Private helper methods with caching and optimization
    @lru_cache(maxsize=128)
    def _get_question_set(self, topic_id, difficulty_level):
        """Get question set with caching"""
        question_set = QuestionSet.query.filter_by(
            topic_id=topic_id,
            difficulty_level=difficulty_level
        ).first()
        
        if not question_set:
            # Fallback to any question set for the topic
            question_set = QuestionSet.query.filter_by(topic_id=topic_id).first()
        
        return question_set
    
    @lru_cache(maxsize=256)
    def _get_questions_for_set(self, question_set_id):
        """Get questions with caching"""
        return Question.query.filter_by(set_id=question_set_id).all()
    
    def _select_questions(self, questions, question_set):
        """Optimized question selection"""
        if not questions:
            return []
        
        num_questions = min(len(questions), question_set.max_questions)
        num_questions = max(num_questions, question_set.min_questions)
        
        return random.sample(questions, min(num_questions, len(questions)))
    
    def _prepare_quiz_data(self, quiz, topic, difficulty_level, selected_questions, question_set):
        """Prepare quiz data structure"""
        return {
            'quiz_id': quiz.quiz_id,
            'topic_name': topic.name,
            'difficulty_level': difficulty_level,
            'questions': [
                {
                    'question_id': q.question_id,
                    'description': q.description,
                    'options': q.options,
                    'marks_worth': q.marks_worth
                }
                for q in selected_questions
            ],
            'total_marks': quiz.total_marks,
            'success_threshold': question_set.success_threshold,
            'time_limit': 30 * len(selected_questions)
        }
    
    def _generate_adaptive_set(self, session_id, topic_id, difficulty_level, set_number):
        """Generate question set for adaptive quiz"""
        session = AdaptiveQuizSession.query.filter_by(session_id=session_id).first()
        if not session:
            return None
        
        # Use the regular quiz generation logic
        quiz_data = self.generate_quiz(session.student_id, topic_id, difficulty_level)
        if not quiz_data:
            return None
        
        # Add adaptive-specific metadata
        quiz_data['set_number'] = set_number
        quiz_data['session_id'] = session_id
        
        return quiz_data
    
    def _get_adaptive_difficulty(self, student_id, topic_id):
        """Determine appropriate difficulty level based on performance"""
        try:
            # Get recent performance with optimized query
            recent_quizzes = Quiz.query.filter_by(
                student_id=student_id,
                topic_id=topic_id
            ).order_by(Quiz.date_taken.desc()).limit(3).all()
            
            if not recent_quizzes:
                return "Easy"  # Start with easy for new students
            
            # Calculate average performance
            avg_score = sum(quiz.score for quiz in recent_quizzes) / len(recent_quizzes)
            
            # Simple difficulty mapping
            if avg_score >= 80:
                return "Hard"
            elif avg_score >= 60:
                return "Medium"
            else:
                return "Easy"
                
        except Exception as e:
            print(f"Error determining difficulty: {e}")
            return "Medium"
    
    def _calculate_next_difficulty(self, current_difficulty, correctness_percentage, is_fast_completion):
        """Calculate next difficulty level for adaptive quiz"""
        if correctness_percentage >= 80 and is_fast_completion:
            # Excellent performance, increase difficulty
            return self.DIFFICULTY_PROGRESSION[current_difficulty]['up'] or current_difficulty
        elif correctness_percentage < 50:
            # Poor performance, decrease difficulty
            return self.DIFFICULTY_PROGRESSION[current_difficulty]['down'] or current_difficulty
        else:
            # Maintain current difficulty
            return current_difficulty
    
    def _update_performance_trends(self, student_id, topic_id, score):
        """Optimized performance trend updates"""
        try:
            trend = PerformanceTrend.query.filter_by(
                student_id=student_id,
                topic_id=topic_id
            ).first()
            
            if not trend:
                trend = PerformanceTrend(
                    student_id=student_id,
                    topic_id=topic_id,
                    proficiency_score=score,
                    trend_graph_data=json.dumps([score])
                )
                db.session.add(trend)
            else:
                # Update existing trend with optimized calculation
                trend_data = json.loads(trend.trend_graph_data) if trend.trend_graph_data else []
                trend_data.append(score)
                trend_data = trend_data[-10:]  # Keep only last 10 scores
                
                # Simple weighted average
                trend.proficiency_score = sum(trend_data) / len(trend_data)
                trend.trend_graph_data = json.dumps(trend_data)
                trend.last_updated = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error updating performance trends: {e}")
    
    def _calculate_session_summary(self, session_data):
        """Calculate session performance summary"""
        sets_completed = session_data.get('sets_completed', [])
        if not sets_completed:
            return {}
        
        total_score = sum(s['score'] for s in sets_completed)
        avg_score = total_score / len(sets_completed)
        
        total_time = sum(s['completion_time'] for s in sets_completed)
        avg_time_per_set = total_time / len(sets_completed)
        
        return {
            'total_sets_completed': len(sets_completed),
            'average_score': round(avg_score, 2),
            'total_time_spent': total_time,
            'average_time_per_set': round(avg_time_per_set, 2),
            'difficulty_changes': len(session_data.get('difficulty_adjustments', []))
        }
    
    def clear_cache(self):
        """Clear the internal caches"""
        self._get_question_set.cache_clear()
        self._get_questions_for_set.cache_clear()
        self._question_cache.clear()