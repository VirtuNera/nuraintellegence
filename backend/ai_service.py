import os
import json
import logging
from google import genai
from google.genai import types
from .models import Student, Quiz, QuizResponse, PerformanceTrend, Topic, Subject
from .topic_prediction_service import topic_prediction_service

class NuraAI:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            self.model = "gemini-2.5-flash"
            self.api_available = True
        else:
            self.client = None
            self.model = None
            self.api_available = False
            logging.warning("GEMINI_API_KEY not found, using fallback responses")
    
    def generate_learner_feedback(self, student_id):
        """Generate personalized feedback for a learner using AI"""
        if not self.api_available:
            return self._get_fallback_feedback()
            
        try:
            # Get learner performance data
            learner = Student.query.filter_by(student_id=student_id).first()
            if not learner:
                return {"error": "Learner not found"}
            
            # Get recent performance
            recent_quizzes = Quiz.query.filter_by(student_id=student_id).order_by(Quiz.date_taken.desc()).limit(5).all()
            performance_trends = PerformanceTrend.query.filter_by(student_id=student_id).all()
            
            # Prepare data for AI analysis
            performance_data = self._prepare_performance_data(recent_quizzes, performance_trends)
            
            prompt = f"""
            You are Nura, an AI learning assistant. Analyze the following learner performance data and provide personalized feedback:
            
            Learner Grade Level: {learner.grade_level}
            Preferred Subjects: {learner.preferred_subjects}
            
            Performance Data: {json.dumps(performance_data)}
            
            Please provide feedback in JSON format with the following structure:
            {{
                "overall_assessment": "Brief overall assessment",
                "strengths": ["List of strengths"],
                "areas_for_improvement": ["List of areas needing work"],
                "study_suggestions": ["Specific study recommendations"],
                "motivation_message": "Encouraging message",
                "next_steps": ["Actionable next steps"]
            }}
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.6,
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return self._get_fallback_feedback()
            
        except Exception as e:
            return self._get_fallback_feedback()
    
    def _get_fallback_feedback(self):
        """Provide fallback feedback when AI is not available"""
        return {
            "overall_assessment": "Great to see you're actively learning! Keep taking quizzes to track your progress.",
            "strengths": ["Consistent learning effort", "Active participation in quizzes"],
            "areas_for_improvement": ["Continue practicing regularly", "Review challenging topics"],
            "study_suggestions": ["Take quizzes in different subjects", "Focus on areas where you scored lower"],
            "motivation_message": "Every quiz you take helps you learn and grow. Keep up the excellent work!",
            "next_steps": ["Try a quiz in a new topic", "Review your recent results"]
        }
    
    def generate_quiz_feedback(self, student_id, quiz_results):
        """Generate AI feedback for a completed quiz"""
        if not self.api_available:
            return self._get_fallback_quiz_feedback(quiz_results)
            
        try:
            prompt = f"""
            You are Nura, an AI learning assistant. Provide feedback for a learner's quiz performance:
            
            Quiz Results: {json.dumps(quiz_results)}
            
            Provide feedback in JSON format:
            {{
                "performance_summary": "Summary of quiz performance",
                "correct_answers_feedback": "Feedback on correct answers",
                "incorrect_answers_feedback": "Feedback on incorrect answers",
                "improvement_tips": ["Specific tips for improvement"],
                "encouragement": "Motivational message",
                "next_quiz_difficulty": "easier/same/harder"
            }}
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.6,
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return self._get_fallback_quiz_feedback(quiz_results)
            
        except Exception as e:
            return self._get_fallback_quiz_feedback(quiz_results)
    
    def _get_fallback_quiz_feedback(self, quiz_results):
        """Provide fallback quiz feedback when AI is not available"""
        score = quiz_results.get('percentage', 0)
        passed = quiz_results.get('passed', False)
        
        if passed:
            return {
                "performance_summary": f"Excellent work! You scored {score}% and passed the quiz.",
                "correct_answers_feedback": "Great job on the questions you answered correctly!",
                "incorrect_answers_feedback": "Review any missed topics to strengthen your understanding.",
                "improvement_tips": ["Keep up the good work", "Try more challenging quizzes"],
                "encouragement": "You're making great progress! Keep learning and growing!",
                "next_quiz_difficulty": "same"
            }
        else:
            return {
                "performance_summary": f"You scored {score}%. Keep practicing to improve!",
                "correct_answers_feedback": "Well done on the questions you got right!",
                "incorrect_answers_feedback": "Focus on reviewing the topics you missed for better understanding.",
                "improvement_tips": ["Practice more questions on challenging topics", "Review the study materials"],
                "encouragement": "Every quiz helps you learn and improve. Keep going!",
                "next_quiz_difficulty": "same"
            }
    
    def adjust_quiz_difficulty(self, student_id, current_performance):
        """Use AI to determine optimal quiz difficulty"""
        if not self.api_available:
            return self._get_fallback_difficulty(current_performance)
            
        try:
            # Get learner's learning pattern
            learner = Student.query.filter_by(student_id=student_id).first()
            performance_trends = PerformanceTrend.query.filter_by(student_id=student_id).all()
            
            if not learner:
                return self._get_fallback_difficulty(current_performance)
            
            prompt = f"""
            Analyze learner performance and recommend quiz difficulty adjustment:
            
            Current Performance: {current_performance}
            Grade Level: {learner.grade_level}
            Historical Trends: {[trend.proficiency_score for trend in performance_trends]}
            
            Respond with JSON:
            {{
                "recommended_difficulty": "very_easy/easy/medium/hard/very_hard",
                "reasoning": "Brief explanation",
                "confidence": 0.0-1.0
            }}
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.6,
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return self._get_fallback_difficulty(current_performance)
            
        except Exception as e:
            return self._get_fallback_difficulty(current_performance)
    
    def _get_fallback_difficulty(self, current_performance):
        """Provide fallback difficulty recommendation"""
        if current_performance >= 85:
            return {
                "recommended_difficulty": "hard",
                "reasoning": "High performance suggests readiness for more challenging content",
                "confidence": 0.8
            }
        elif current_performance >= 70:
            return {
                "recommended_difficulty": "medium",
                "reasoning": "Good performance suggests current difficulty is appropriate",
                "confidence": 0.7
            }
        elif current_performance >= 50:
            return {
                "recommended_difficulty": "easy",
                "reasoning": "Moderate performance suggests need for easier content",
                "confidence": 0.7
            }
        else:
            return {
                "recommended_difficulty": "very_easy",
                "reasoning": "Low performance suggests need for foundational review",
                "confidence": 0.8
            }
    
    def generate_educator_insights(self, class_data):
        """Generate insights for educators about their class"""
        if not self.api_available:
            return self._get_fallback_educator_insights(class_data)
            
        try:
            prompt = f"""
            You are Nura, an AI assistant for educators. Analyze class performance data and provide insights:
            
            Class Data: {json.dumps(class_data)}
            
            Provide insights in JSON format:
            {{
                "class_overview": "Overall class performance summary",
                "top_performers": ["Learners performing well"],
                "learners_needing_help": ["Learners who need attention"],
                "subject_insights": {{"subject": "insights"}},
                "recommendations": ["Actionable recommendations for the educator"],
                "intervention_suggestions": ["Specific intervention strategies"]
            }}
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.6,
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return self._get_fallback_educator_insights(class_data)
            
        except Exception as e:
            return self._get_fallback_educator_insights(class_data)
    
    def _get_fallback_educator_insights(self, class_data):
        """Provide fallback educator insights when AI is not available"""
        return {
            "class_overview": "Your class is actively engaging with the learning platform. Continue monitoring individual progress.",
            "top_performers": ["Check recent quiz scores to identify top performers"],
            "learners_needing_help": ["Review learners with lower quiz scores for additional support"],
            "subject_insights": {"general": "Monitor performance across different subjects to identify areas of strength and weakness"},
            "recommendations": [
                "Review individual learner progress regularly",
                "Provide additional practice for challenging topics",
                "Celebrate learner achievements to maintain motivation"
            ],
            "intervention_suggestions": [
                "Offer one-on-one support for struggling learners",
                "Create study groups for peer learning",
                "Adjust quiz difficulty based on performance"
            ]
        }
    
    def _prepare_performance_data(self, recent_quizzes, performance_trends):
        """Prepare performance data for AI analysis"""
        quiz_data = []
        for quiz in recent_quizzes:
            quiz_data.append({
                'topic': quiz.topic.name,
                'subject': quiz.topic.subject.name,
                'score': quiz.score,
                'total_marks': quiz.total_marks,
                'date': quiz.date_taken.isoformat(),
                'time_taken': quiz.time_taken
            })
        
        trend_data = []
        for trend in performance_trends:
            trend_data.append({
                'topic': trend.topic.name,
                'subject': trend.topic.subject.name,
                'proficiency_score': trend.proficiency_score,
                'trend_data': trend.trend_graph_data
            })
        
        return {
            'recent_quizzes': quiz_data,
            'performance_trends': trend_data
        }
    
    def predict_learning_topics(self, student_id):
        """Predict optimal learning topics for a learner using machine learning"""
        try:
            # Get ML-based topic prediction
            ml_prediction = topic_prediction_service.get_learning_recommendations(student_id)
            
            if not ml_prediction.get('success'):
                return ml_prediction
            
            # Enhance with AI insights if available
            if self.api_available:
                prediction_data = ml_prediction['prediction']
                
                prompt = f"""
                You are Nura, an AI learning assistant. A machine learning model has predicted the following topic recommendations for a learner:
                
                ML Prediction: {json.dumps(prediction_data)}
                
                Please provide enhanced learning insights in JSON format:
                {{
                    "ai_insights": "Additional insights from AI analysis",
                    "learning_strategy": "Recommended learning approach",
                    "motivation_message": "Encouraging message for the learner",
                    "study_techniques": ["Specific study techniques for the recommended topic"],
                    "progress_tracking": "How to track improvement in this area"
                }}
                """
                
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.7,
                            response_mime_type="application/json"
                        )
                    )
                    
                    if response.text:
                        ai_insights = json.loads(response.text)
                        ml_prediction['ai_insights'] = ai_insights
                        
                except Exception as e:
                    logging.error(f"Error generating AI insights for topic prediction: {str(e)}")
                    # Continue with ML prediction only
            
            return ml_prediction
            
        except Exception as e:
            logging.error(f"Error in predict_learning_topics: {str(e)}")
            return {
                'success': False,
                'message': 'Unable to generate topic predictions. Please try again later.'
            }
    
    def get_topic_performance_analysis(self, student_id):
        """Get detailed performance analysis for topic prediction"""
        try:
            # Get performance metrics from ML service
            metrics = topic_prediction_service.get_learner_performance_metrics(student_id)
            
            if not metrics:
                return {
                    'success': False,
                    'message': 'No performance data available for analysis.'
                }
            
            # Calculate additional insights
            total_questions = metrics['total_qs']
            if total_questions == 0:
                return {
                    'success': False,
                    'message': 'Please complete some quizzes first to get performance analysis.'
                }
            
            # Calculate performance percentages
            add_total = metrics['total_qs_addition']
            sub_total = metrics['total_qs_substraction']
            mul_total = metrics['total_qs_multipication']
            
            add_accuracy = (metrics['total_answer_right_addition'] / max(add_total, 1)) * 100
            sub_accuracy = (metrics['total_answer_right_subtraction'] / max(sub_total, 1)) * 100
            mul_accuracy = (metrics['total_answer_right_multplication'] / max(mul_total, 1)) * 100
            
            overall_accuracy = ((metrics['total_answer_right_addition'] + 
                               metrics['total_answer_right_subtraction'] + 
                               metrics['total_answer_right_multplication']) / total_questions) * 100
            
            analysis = {
                'success': True,
                'total_questions': total_questions,
                'overall_accuracy': round(overall_accuracy, 1),
                'topic_breakdown': {
                    'addition': {
                        'questions': add_total,
                        'correct': metrics['total_answer_right_addition'],
                        'accuracy': round(add_accuracy, 1)
                    },
                    'subtraction': {
                        'questions': sub_total,
                        'correct': metrics['total_answer_right_subtraction'],
                        'accuracy': round(sub_accuracy, 1)
                    },
                    'multiplication': {
                        'questions': mul_total,
                        'correct': metrics['total_answer_right_multplication'],
                        'accuracy': round(mul_accuracy, 1)
                    }
                },
                'performance_level': self._classify_performance_level(overall_accuracy),
                'recommendations': self._get_performance_recommendations(add_accuracy, sub_accuracy, mul_accuracy)
            }
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error in get_topic_performance_analysis: {str(e)}")
            return {
                'success': False,
                'message': 'Unable to analyze performance. Please try again later.'
            }
    
    def _classify_performance_level(self, accuracy):
        """Classify performance level based on accuracy"""
        if accuracy >= 90:
            return "Excellent"
        elif accuracy >= 80:
            return "Good"
        elif accuracy >= 70:
            return "Satisfactory"
        elif accuracy >= 60:
            return "Needs Improvement"
        else:
            return "Requires Attention"
    
    def _get_performance_recommendations(self, add_accuracy, sub_accuracy, mul_accuracy):
        """Get performance-based recommendations"""
        recommendations = []
        
        if add_accuracy < 70:
            recommendations.append("Focus on addition practice - try starting with simpler problems")
        elif add_accuracy > 85:
            recommendations.append("Great job with addition! Try more challenging addition problems")
        
        if sub_accuracy < 70:
            recommendations.append("Work on subtraction skills - practice with visual aids")
        elif sub_accuracy > 85:
            recommendations.append("Excellent subtraction skills! Try word problems with subtraction")
        
        if mul_accuracy < 70:
            recommendations.append("Practice multiplication tables and basic multiplication")
        elif mul_accuracy > 85:
            recommendations.append("Strong multiplication skills! Try multi-digit multiplication")
        
        if not recommendations:
            recommendations.append("Keep up the good work! Continue practicing all topics regularly")
        
        return recommendations
