import random
import json
from datetime import datetime
from app import db
from models import Quiz, QuizResponse, Question, QuestionSet, Topic, Student, PerformanceTrend
from ai_service import NuraAI

class QuizEngine:
    def __init__(self):
        self.nura_ai = NuraAI()
    
    def generate_adaptive_quiz(self, student_id, topic_id):
        """Generate an adaptive quiz based on student's performance history"""
        try:
            student = Student.query.filter_by(student_id=student_id).first()
            topic = Topic.query.filter_by(topic_id=topic_id).first()
            
            if not student or not topic:
                return None
            
            # Determine appropriate difficulty level
            difficulty_level = self._get_adaptive_difficulty(student_id, topic_id)
            
            # Get question set for the topic and difficulty
            question_set = QuestionSet.query.filter_by(
                topic_id=topic_id,
                difficulty_level=difficulty_level
            ).first()
            
            if not question_set:
                # Fall back to any available question set for the topic
                question_set = QuestionSet.query.filter_by(topic_id=topic_id).first()
            
            if not question_set:
                return None
            
            # Get questions from the set
            questions = Question.query.filter_by(set_id=question_set.question_set_id).all()
            
            if not questions:
                return None
            
            # Select random questions based on min/max constraints
            num_questions = min(len(questions), question_set.max_questions)
            num_questions = max(num_questions, question_set.min_questions)
            selected_questions = random.sample(questions, min(num_questions, len(questions)))
            
            # Create quiz record
            quiz = Quiz(
                student_id=student_id,
                topic_id=topic_id,
                question_set_id=question_set.question_set_id,
                total_marks=sum(q.marks_worth for q in selected_questions)
            )
            db.session.add(quiz)
            db.session.commit()
            
            # Prepare quiz data
            quiz_data = {
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
                'time_limit': 30 * len(selected_questions)  # 30 seconds per question
            }
            
            return quiz_data
            
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return None
    
    def process_quiz_submission(self, student_id, quiz_data, answers):
        """Process quiz submission and calculate results"""
        try:
            quiz = Quiz.query.filter_by(quiz_id=quiz_data['quiz_id']).first()
            if not quiz:
                return None
            
            total_score = 0
            correct_answers = 0
            total_questions = len(quiz_data['questions'])
            
            # Process each answer
            for question_data in quiz_data['questions']:
                question_id = question_data['question_id']
                question = Question.query.filter_by(question_id=question_id).first()
                
                selected_option = answers.get(f'question_{question_id}', '')
                is_correct = selected_option == question.correct_option
                
                print(f"Question {question_id}: Selected='{selected_option}', Correct='{question.correct_option}', Match={is_correct}")
                
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
            quiz.score = (total_score / quiz.total_marks) * 100 if quiz.total_marks > 0 else 0
            quiz.date_taken = datetime.utcnow()
            
            db.session.commit()
            
            # Update performance trends
            self._update_performance_trends(student_id, quiz.topic_id, quiz.score)
            
            # Prepare results
            results = {
                'quiz_id': quiz.quiz_id,
                'score': quiz.score,
                'total_marks': quiz.total_marks,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'percentage': round(quiz.score, 2),
                'passed': quiz.score >= quiz_data['success_threshold'],
                'success_threshold': quiz_data['success_threshold']
            }
            
            return results
            
        except Exception as e:
            print(f"Error processing quiz submission: {e}")
            return None
    
    def _get_adaptive_difficulty(self, student_id, topic_id):
        """Determine appropriate difficulty level based on student's performance"""
        try:
            # Get student's recent performance in this topic
            recent_quizzes = Quiz.query.filter_by(
                student_id=student_id,
                topic_id=topic_id
            ).order_by(Quiz.date_taken.desc()).limit(3).all()
            
            if not recent_quizzes:
                # New student, start with easy difficulty
                return "easy"
            
            # Calculate average performance
            avg_score = sum(quiz.score for quiz in recent_quizzes) / len(recent_quizzes)
            
            # Use AI to determine difficulty
            ai_recommendation = self.nura_ai.adjust_quiz_difficulty(student_id, avg_score)
            
            return ai_recommendation.get('recommended_difficulty', 'medium')
            
        except Exception as e:
            print(f"Error determining difficulty: {e}")
            return "medium"
    
    def _update_performance_trends(self, student_id, topic_id, score):
        """Update performance trends for analytics"""
        try:
            # Get or create performance trend record
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
                # Update existing trend
                trend_data = json.loads(trend.trend_graph_data) if trend.trend_graph_data else []
                trend_data.append(score)
                
                # Keep only last 10 scores
                trend_data = trend_data[-10:]
                
                # Calculate new proficiency score (weighted average)
                weights = [0.4, 0.3, 0.2, 0.1]  # Recent scores have more weight
                weighted_score = 0
                total_weight = 0
                
                for i, score_val in enumerate(reversed(trend_data)):
                    if i < len(weights):
                        weighted_score += score_val * weights[i]
                        total_weight += weights[i]
                    else:
                        break
                
                trend.proficiency_score = weighted_score / total_weight if total_weight > 0 else score
                trend.trend_graph_data = json.dumps(trend_data)
                trend.last_updated = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error updating performance trends: {e}")
