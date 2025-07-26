import json
import random
from datetime import datetime, timedelta
from app import db
from models import (
    Quiz, QuizResponse, Question, QuestionSet, Topic, Student, 
    PerformanceTrend, AdaptiveQuizSession
)
from ai_service import NuraAI

class AdaptiveQuizEngine:
    """
    Advanced adaptive quiz engine that dynamically adjusts difficulty
    based on student performance across multiple question sets.
    """
    
    DIFFICULTY_LEVELS = ['Very Easy', 'Easy', 'Medium', 'Hard', 'Very Hard']
    
    def __init__(self):
        self.nura_ai = NuraAI()
    
    def start_adaptive_session(self, student_id, topic_id, initial_difficulty, total_sets=5):
        """
        Start a new adaptive quiz session with the selected initial difficulty.
        
        Args:
            student_id: Student's unique identifier
            topic_id: Topic for the quiz session
            initial_difficulty: Student's chosen starting difficulty
            total_sets: Number of question sets to complete
            
        Returns:
            Dict containing session data and first question set
        """
        try:
            # Validate inputs
            if initial_difficulty not in self.DIFFICULTY_LEVELS:
                raise ValueError(f"Invalid difficulty level: {initial_difficulty}")
            
            student = Student.query.filter_by(student_id=student_id).first()
            topic = Topic.query.filter_by(topic_id=topic_id).first()
            
            if not student or not topic:
                return None
            
            # Create new adaptive quiz session
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
            first_set = self._generate_question_set(
                session.session_id, 
                topic_id, 
                initial_difficulty,
                set_number=1
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
    
    def _generate_question_set(self, session_id, topic_id, difficulty_level, set_number):
        """
        Generate a question set for the specified difficulty level.
        
        Args:
            session_id: Adaptive quiz session ID
            topic_id: Topic identifier
            difficulty_level: Current difficulty level
            set_number: Current set number
            
        Returns:
            Dict containing question set data
        """
        try:
            # Get question set for the topic and difficulty
            question_set = QuestionSet.query.filter_by(
                topic_id=topic_id,
                difficulty_level=difficulty_level
            ).first()
            
            if not question_set:
                # Try to find any question set for the topic
                question_set = QuestionSet.query.filter_by(topic_id=topic_id).first()
            
            if not question_set:
                return None
            
            # Get questions from the set
            questions = Question.query.filter_by(set_id=question_set.question_set_id).all()
            
            if not questions:
                return None
            
            # Select random questions based on constraints
            num_questions = min(len(questions), question_set.max_questions)
            num_questions = max(num_questions, question_set.min_questions)
            selected_questions = random.sample(questions, min(num_questions, len(questions)))
            
            # Create quiz record for this set
            quiz = Quiz(
                student_id=AdaptiveQuizSession.query.filter_by(session_id=session_id).first().student_id,
                topic_id=topic_id,
                question_set_id=question_set.question_set_id,
                total_marks=sum(q.marks_worth for q in selected_questions)
            )
            db.session.add(quiz)
            db.session.commit()
            
            # Prepare question set data
            question_set_data = {
                'quiz_id': quiz.quiz_id,
                'set_number': set_number,
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
            
            return question_set_data
            
        except Exception as e:
            print(f"Error generating question set: {e}")
            return None
    
    def process_set_submission(self, session_id, quiz_data, answers, completion_time):
        """
        Process the submission of a question set and determine next difficulty.
        
        Args:
            session_id: Adaptive quiz session ID
            quiz_data: Data for the completed question set
            answers: Student's answers
            completion_time: Time taken to complete the set (in seconds)
            
        Returns:
            Dict containing results and next set data (if applicable)
        """
        try:
            session = AdaptiveQuizSession.query.filter_by(session_id=session_id).first()
            if not session:
                return None
            
            # Process the quiz submission
            quiz = Quiz.query.filter_by(quiz_id=quiz_data['quiz_id']).first()
            if not quiz:
                return None
            
            # Calculate performance metrics
            total_score = 0
            correct_answers = 0
            total_questions = len(quiz_data['questions'])
            
            # Process each answer
            for question_data in quiz_data['questions']:
                question_id = question_data['question_id']
                question = Question.query.filter_by(question_id=question_id).first()
                
                selected_option = answers.get(f'question_{question_id}', '')
                is_correct = selected_option == question.correct_option
                
                if is_correct:
                    total_score += question.marks_worth
                    correct_answers += 1
                
                # Create quiz response record
                response = QuizResponse(
                    quiz_id=quiz.quiz_id,
                    question_id=question_id,
                    selected_option=selected_option,
                    is_correct=is_correct,
                    time_taken=completion_time // total_questions  # Average time per question
                )
                db.session.add(response)
            
            # Update quiz record
            quiz.score = (total_score / quiz.total_marks) * 100 if quiz.total_marks > 0 else 0
            quiz.date_taken = datetime.utcnow()
            quiz.time_taken = completion_time
            
            # Calculate performance metrics
            correctness_percentage = (correct_answers / total_questions) * 100
            average_time_per_question = completion_time / total_questions
            
            # Determine if completion was fast (less than 20 seconds per question)
            is_fast_completion = average_time_per_question < 20
            
            # Update session data
            session_data = json.loads(session.session_data)
            
            set_result = {
                'set_number': session.current_set,
                'difficulty_level': session.current_difficulty,
                'quiz_id': quiz.quiz_id,
                'score': quiz.score,
                'correctness_percentage': correctness_percentage,
                'completion_time': completion_time,
                'average_time_per_question': average_time_per_question,
                'is_fast_completion': is_fast_completion,
                'total_questions': total_questions,
                'correct_answers': correct_answers
            }
            
            session_data['sets_completed'].append(set_result)
            session_data['performance_history'].append({
                'set_number': session.current_set,
                'score': quiz.score,
                'time': completion_time
            })
            
            # Determine next difficulty level
            next_difficulty = self._calculate_next_difficulty(
                session.current_difficulty,
                correctness_percentage,
                is_fast_completion
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
            
            # Prepare results
            results = {
                'set_results': set_result,
                'session_progress': {
                    'current_set': session.current_set - 1,  # Just completed
                    'total_sets': session.total_sets,
                    'next_set': session.current_set,
                    'current_difficulty': session.current_difficulty,
                    'next_difficulty': next_difficulty
                }
            }
            
            # Check if session is complete
            if session.current_set > session.total_sets:
                results['session_complete'] = True
                results['final_results'] = self._finalize_session(session_id)
            else:
                # Generate next question set
                next_set = self._generate_question_set(
                    session_id,
                    session.topic_id,
                    next_difficulty,
                    session.current_set
                )
                results['next_question_set'] = next_set
                results['session_complete'] = False
            
            return results
            
        except Exception as e:
            print(f"Error processing set submission: {e}")
            return None
    
    def _calculate_next_difficulty(self, current_difficulty, correctness_percentage, is_fast_completion):
        """
        Calculate the next difficulty level based on performance thresholds.
        
        Performance Rules:
        - >80% correct AND fast completion → increase difficulty
        - 60-79% correct → maintain current difficulty
        - <60% correct → decrease difficulty
        - High performance at highest level → maintain
        - Low performance at lowest level → maintain
        """
        current_index = self.DIFFICULTY_LEVELS.index(current_difficulty)
        
        # High performance: increase difficulty
        if correctness_percentage >= 80 and is_fast_completion:
            if current_index < len(self.DIFFICULTY_LEVELS) - 1:
                return self.DIFFICULTY_LEVELS[current_index + 1]
        
        # Low performance: decrease difficulty
        elif correctness_percentage < 60:
            if current_index > 0:
                return self.DIFFICULTY_LEVELS[current_index - 1]
        
        # Medium performance (60-79%): maintain current difficulty
        return current_difficulty
    
    def _finalize_session(self, session_id):
        """
        Finalize the adaptive quiz session and calculate final proficiency score.
        
        Args:
            session_id: Adaptive quiz session ID
            
        Returns:
            Dict containing final session results
        """
        try:
            session = AdaptiveQuizSession.query.filter_by(session_id=session_id).first()
            if not session:
                return None
            
            session_data = json.loads(session.session_data)
            sets_completed = session_data['sets_completed']
            
            if not sets_completed:
                return None
            
            # Calculate final proficiency score
            # Use weighted average with more weight on later sets
            total_weighted_score = 0
            total_weight = 0
            
            for i, set_result in enumerate(sets_completed):
                # Weight increases with set number (later sets more important)
                weight = (i + 1) * 0.2
                total_weighted_score += set_result['score'] * weight
                total_weight += weight
            
            final_proficiency = total_weighted_score / total_weight if total_weight > 0 else 0
            
            # Bonus for difficulty progression
            difficulty_bonus = 0
            if session_data['difficulty_adjustments']:
                for adjustment in session_data['difficulty_adjustments']:
                    if self.DIFFICULTY_LEVELS.index(adjustment['to_difficulty']) > \
                       self.DIFFICULTY_LEVELS.index(adjustment['from_difficulty']):
                        difficulty_bonus += 5  # 5% bonus for each difficulty increase
            
            final_proficiency = min(100, final_proficiency + difficulty_bonus)
            
            # Update session
            session.final_proficiency_score = final_proficiency
            session.is_completed = True
            session.end_time = datetime.utcnow()
            
            # Update student's overall proficiency for this topic
            self._update_student_proficiency(session.student_id, session.topic_id, final_proficiency)
            
            db.session.commit()
            
            # Prepare final results
            final_results = {
                'session_id': session_id,
                'final_proficiency_score': final_proficiency,
                'initial_difficulty': session.initial_difficulty,
                'final_difficulty': session.current_difficulty,
                'total_sets_completed': len(sets_completed),
                'total_time': (session.end_time - session.start_time).total_seconds(),
                'sets_summary': sets_completed,
                'difficulty_adjustments': session_data['difficulty_adjustments'],
                'performance_trend': [s['score'] for s in sets_completed]
            }
            
            return final_results
            
        except Exception as e:
            print(f"Error finalizing session: {e}")
            return None
    
    def _update_student_proficiency(self, student_id, topic_id, final_proficiency):
        """Update the student's proficiency score for the topic."""
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
                    proficiency_score=final_proficiency,
                    trend_graph_data=json.dumps([final_proficiency])
                )
                db.session.add(trend)
            else:
                # Update existing trend
                trend_data = json.loads(trend.trend_graph_data) if trend.trend_graph_data else []
                trend_data.append(final_proficiency)
                
                # Keep only last 10 scores
                trend_data = trend_data[-10:]
                
                # Update proficiency score (average of recent scores)
                trend.proficiency_score = sum(trend_data) / len(trend_data)
                trend.trend_graph_data = json.dumps(trend_data)
                trend.last_updated = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error updating student proficiency: {e}")
    
    def get_session_status(self, session_id):
        """Get current status of an adaptive quiz session."""
        try:
            session = AdaptiveQuizSession.query.filter_by(session_id=session_id).first()
            if not session:
                return None
            
            session_data = json.loads(session.session_data)
            
            return {
                'session_id': session_id,
                'student_id': session.student_id,
                'topic_id': session.topic_id,
                'current_set': session.current_set,
                'total_sets': session.total_sets,
                'current_difficulty': session.current_difficulty,
                'initial_difficulty': session.initial_difficulty,
                'is_completed': session.is_completed,
                'sets_completed': session_data.get('sets_completed', []),
                'difficulty_adjustments': session_data.get('difficulty_adjustments', [])
            }
            
        except Exception as e:
            print(f"Error getting session status: {e}")
            return None