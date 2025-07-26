"""
Topic Prediction Service for Nura AI
Uses machine learning to predict which topics students should focus on
based on their performance patterns.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import logging
from typing import Dict, List, Optional, Tuple
from app import app, db
from models import Student, Quiz, QuizResponse, Question, QuestionSet, Topic, Subject

class TopicPredictionService:
    """Service for predicting optimal topics for student learning"""
    
    def __init__(self):
        self.model = None
        self.feature_columns = [
            'total_qs',
            'total_qs_addition',
            'total_qs_substraction',
            'total_qs_multipication',
            'total_answer_right_addition',
            'total_answer_right_subtraction',
            'total_answer_right_multplication'
        ]
        self.is_trained = False
        self._train_model()
    
    def _train_model(self):
        """Train the prediction model using the provided score data"""
        try:
            # Load training data
            data = pd.read_csv('score_data.csv')
            
            # Prepare features and target
            X = data[self.feature_columns]
            y = data['recommend']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model = LogisticRegression(max_iter=200, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.is_trained = True
            logging.info(f"Topic prediction model trained successfully with {accuracy:.2%} accuracy")
            
        except Exception as e:
            logging.error(f"Error training topic prediction model: {str(e)}")
            self.is_trained = False
    
    def get_student_performance_metrics(self, student_id: str) -> Optional[Dict]:
        """Extract performance metrics for a student from the database"""
        try:
            # Get student's quiz history
            student = Student.query.filter_by(student_id=student_id).first()
            if not student:
                return None
            
            quizzes = Quiz.query.filter_by(student_id=student_id).all()
            if not quizzes:
                return None
            
            # Initialize counters
            metrics = {
                'total_qs': 0,
                'total_qs_addition': 0,
                'total_qs_substraction': 0,
                'total_qs_multipication': 0,
                'total_answer_right_addition': 0,
                'total_answer_right_subtraction': 0,
                'total_answer_right_multplication': 0
            }
            
            # Analyze each quiz
            for quiz in quizzes:
                # Get quiz responses
                responses = QuizResponse.query.filter_by(quiz_id=quiz.quiz_id).all()
                
                for response in responses:
                    # Get question details
                    question = Question.query.filter_by(question_id=response.question_id).first()
                    if not question:
                        continue
                    
                    # Get question set to determine topic
                    question_set = QuestionSet.query.filter_by(question_set_id=question.set_id).first()
                    if not question_set:
                        continue
                    
                    # Get topic details
                    topic = Topic.query.filter_by(topic_id=question_set.topic_id).first()
                    if not topic:
                        continue
                    
                    # Get subject details
                    subject = Subject.query.filter_by(subject_id=topic.subject_id).first()
                    if not subject:
                        continue
                    
                    # Count questions and correct answers by topic
                    metrics['total_qs'] += 1
                    
                    subject_name = subject.name.lower()
                    topic_name = topic.name.lower()
                    
                    # Categorize by math operation
                    if 'sum' in subject_name or 'addition' in topic_name:
                        metrics['total_qs_addition'] += 1
                        if response.is_correct:
                            metrics['total_answer_right_addition'] += 1
                    elif 'subtraction' in subject_name or 'subtraction' in topic_name:
                        metrics['total_qs_substraction'] += 1
                        if response.is_correct:
                            metrics['total_answer_right_subtraction'] += 1
                    elif 'multiplication' in subject_name or 'multiplication' in topic_name:
                        metrics['total_qs_multipication'] += 1
                        if response.is_correct:
                            metrics['total_answer_right_multplication'] += 1
            
            return metrics
            
        except Exception as e:
            logging.error(f"Error extracting student performance metrics: {str(e)}")
            return None
    
    def predict_recommended_topic(self, student_id: str) -> Optional[Dict]:
        """Predict the recommended topic for a student based on their performance"""
        if not self.is_trained:
            return None
        
        try:
            # Get student performance metrics
            metrics = self.get_student_performance_metrics(student_id)
            if not metrics:
                return None
            
            # Create DataFrame for prediction
            input_data = pd.DataFrame([metrics])
            
            # Make prediction
            predicted_topic = self.model.predict(input_data)[0]
            prediction_probabilities = self.model.predict_proba(input_data)[0]
            
            # Get class labels
            classes = self.model.classes_
            
            # Create probability dictionary
            prob_dict = {class_name: float(prob) for class_name, prob in zip(classes, prediction_probabilities)}
            
            # Get confidence score (highest probability)
            confidence = max(prediction_probabilities)
            
            return {
                'student_id': student_id,
                'recommended_topic': predicted_topic,
                'confidence': float(confidence),
                'probabilities': prob_dict,
                'performance_metrics': metrics,
                'explanation': self._generate_explanation(predicted_topic, metrics)
            }
            
        except Exception as e:
            logging.error(f"Error predicting topic for student {student_id}: {str(e)}")
            return None
    
    def _generate_explanation(self, predicted_topic: str, metrics: Dict) -> str:
        """Generate a human-readable explanation for the prediction"""
        
        total_questions = metrics['total_qs']
        if total_questions == 0:
            return "No performance data available for prediction."
        
        # Calculate accuracy rates
        add_accuracy = (metrics['total_answer_right_addition'] / max(metrics['total_qs_addition'], 1)) * 100
        sub_accuracy = (metrics['total_answer_right_subtraction'] / max(metrics['total_qs_substraction'], 1)) * 100
        mul_accuracy = (metrics['total_answer_right_multplication'] / max(metrics['total_qs_multipication'], 1)) * 100
        
        explanation = f"Based on {total_questions} questions answered:\n"
        explanation += f"- Addition: {add_accuracy:.1f}% correct ({metrics['total_answer_right_addition']}/{metrics['total_qs_addition']})\n"
        explanation += f"- Subtraction: {sub_accuracy:.1f}% correct ({metrics['total_answer_right_subtraction']}/{metrics['total_qs_substraction']})\n"
        explanation += f"- Multiplication: {mul_accuracy:.1f}% correct ({metrics['total_answer_right_multplication']}/{metrics['total_qs_multipication']})\n\n"
        
        if predicted_topic.lower() == 'addition':
            explanation += "Recommended focus: Addition - You may need more practice with addition problems."
        elif predicted_topic.lower() == 'subtraction':
            explanation += "Recommended focus: Subtraction - You may need more practice with subtraction problems."
        elif predicted_topic.lower() == 'multiplication':
            explanation += "Recommended focus: Multiplication - You may need more practice with multiplication problems."
        else:
            explanation += f"Recommended focus: {predicted_topic} - Continue practicing this topic area."
        
        return explanation
    
    def get_learning_recommendations(self, student_id: str) -> Dict:
        """Get comprehensive learning recommendations for a student"""
        
        prediction = self.predict_recommended_topic(student_id)
        if not prediction:
            return {
                'success': False,
                'message': 'Unable to generate recommendations. Please complete more quizzes first.'
            }
        
        # Get available topics and question sets for the recommended topic
        recommended_topic = prediction['recommended_topic']
        
        # Find related topics in the database
        related_topics = []
        subjects = Subject.query.all()
        
        # Create topic mapping for better matching
        topic_mapping = {
            'addition': ['sum', 'simple sum', 'advance sum'],
            'subtraction': ['subtraction', 'simple subtraction'],
            'multiplication': ['multiplication', 'simple multiplication', 'times tables'],
            'division': ['division', 'simple division', 'division remainder'],
            'fractions': ['fractions', 'fraction addition', 'fraction simplification']
        }
        
        for subject in subjects:
            topics = Topic.query.filter_by(subject_id=subject.subject_id).all()
            for topic in topics:
                # Check direct match or mapped terms
                topic_match = False
                
                # Direct matching
                if (recommended_topic.lower() in topic.name.lower() or
                    topic.name.lower() in recommended_topic.lower() or
                    recommended_topic.lower() in subject.name.lower()):
                    topic_match = True
                
                # Mapped matching
                if recommended_topic.lower() in topic_mapping:
                    mapped_terms = topic_mapping[recommended_topic.lower()]
                    for term in mapped_terms:
                        if term.lower() in topic.name.lower() or term.lower() in subject.name.lower():
                            topic_match = True
                            break
                
                if topic_match:
                    question_sets = QuestionSet.query.filter_by(topic_id=topic.topic_id).all()
                    if question_sets:
                        related_topics.append({
                            'topic_id': topic.topic_id,
                            'topic_name': topic.name,
                            'subject_name': subject.name,
                            'difficulty_level': topic.difficulty_level,
                            'question_sets': len(question_sets)
                        })
        
        return {
            'success': True,
            'prediction': prediction,
            'related_topics': related_topics,
            'study_plan': self._generate_study_plan(prediction, related_topics)
        }
    
    def _generate_study_plan(self, prediction: Dict, related_topics: List[Dict]) -> List[Dict]:
        """Generate a personalized study plan based on prediction"""
        
        recommended_topic = prediction['recommended_topic']
        confidence = prediction['confidence']
        
        study_plan = []
        
        # High confidence - focus on the recommended topic
        if confidence > 0.8:
            matching_topics = [topic for topic in related_topics if 
                             recommended_topic.lower() in topic['topic_name'].lower() or
                             topic['topic_name'].lower() in recommended_topic.lower()]
            topic_id = matching_topics[0]['topic_id'] if matching_topics else (related_topics[0]['topic_id'] if related_topics else None)
            
            # Use the actual topic name from database for better clarity
            display_topic = matching_topics[0]['topic_name'] if matching_topics else (related_topics[0]['topic_name'] if related_topics else recommended_topic)
            
            study_plan.append({
                'priority': 'High',
                'action': f'Focus on {display_topic}',
                'description': f'Complete practice quizzes in {display_topic} to improve your skills.',
                'topic_id': topic_id,
                'topics': matching_topics if matching_topics else related_topics
            })
        
        # Medium confidence - practice recommended topic but also review others
        elif confidence > 0.6:
            matching_topics = [topic for topic in related_topics if 
                             recommended_topic.lower() in topic['topic_name'].lower() or
                             topic['topic_name'].lower() in recommended_topic.lower()]
            topic_id = matching_topics[0]['topic_id'] if matching_topics else (related_topics[0]['topic_id'] if related_topics else None)
            
            # Use the actual topic name from database for better clarity
            display_topic = matching_topics[0]['topic_name'] if matching_topics else (related_topics[0]['topic_name'] if related_topics else recommended_topic)
            
            study_plan.append({
                'priority': 'Medium',
                'action': f'Practice {display_topic} with review',
                'description': f'Focus on {display_topic} but also review other math topics.',
                'topic_id': topic_id,
                'topics': related_topics
            })
        
        # Low confidence - general practice recommended
        else:
            topic_id = related_topics[0]['topic_id'] if related_topics else None
            study_plan.append({
                'priority': 'Low',
                'action': 'General practice',
                'description': 'Continue practicing all math topics to build a stronger foundation.',
                'topic_id': topic_id,
                'topics': related_topics
            })
        
        return study_plan

# Global instance
topic_prediction_service = TopicPredictionService()