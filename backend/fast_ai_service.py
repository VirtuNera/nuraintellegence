"""
Fast AI service with minimal API calls and aggressive caching
"""

import logging
from .performance_cache import cached, cache

class FastAI:
    """Optimized AI service that prioritizes speed over complex responses"""
    
    def __init__(self):
        self.api_available = False  # Start with fallback mode for speed
        
    @cached(ttl=1800)  # 30-minute cache for AI responses
    def generate_learner_feedback(self, student_id):
        """Generate comprehensive learner feedback matching template expectations"""
        # Use pre-generated responses with proper structure for AI Support template
        feedback_templates = [
            {
                "overall_assessment": "You're making excellent progress in your learning journey! Your consistent participation shows dedication to improving your knowledge and skills.",
                "strengths": [
                    "Shows consistent participation in quizzes and learning activities",
                    "Demonstrates strong foundational understanding of key concepts", 
                    "Actively engages with learning materials and seeks improvement"
                ],
                "areas_for_improvement": [
                    "Focus on challenging topics that need more practice and attention",
                    "Review incorrect answers thoroughly to learn from mistakes",
                    "Spend additional time on topics with lower accuracy scores"
                ],
                "study_suggestions": [
                    "Take daily practice quizzes for 15-20 minutes to build consistency",
                    "Review and revisit topics where you scored below 75%",
                    "Challenge yourself with higher difficulty levels as you improve",
                    "Use the Topic Predictions feature to get personalized recommendations"
                ],
                "motivation_message": "Every step forward is meaningful progress. Trust in your ability to grow and learn new things!"
            },
            {
                "overall_assessment": "Great effort! Your quiz performance demonstrates real dedication to learning. You're building solid knowledge foundations across multiple subjects.",
                "strengths": [
                    "Maintains steady improvement trend over time",
                    "Shows willingness to tackle challenging topics",
                    "Demonstrates good problem-solving approach"
                ],
                "areas_for_improvement": [
                    "Work on time management during quiz sessions",
                    "Practice more complex problems to build confidence",
                    "Focus on areas with inconsistent performance"
                ],
                "study_suggestions": [
                    "Set specific daily learning goals and track progress",
                    "Use active recall techniques when reviewing material",
                    "Practice explaining concepts to reinforce understanding",
                    "Take advantage of AI-powered topic recommendations"
                ],
                "motivation_message": "Learning is a journey of continuous growth. You're doing fantastic - keep pushing forward!"
            },
            {
                "overall_assessment": "Wonderful work! You're building strong knowledge foundations and showing real commitment to your educational goals.",
                "strengths": [
                    "Consistently completes learning activities",
                    "Shows improvement in problem-solving skills",
                    "Demonstrates curiosity and engagement with content"
                ],
                "areas_for_improvement": [
                    "Continue practicing to build speed and accuracy",
                    "Focus on connecting concepts across different topics",
                    "Build confidence through regular review and practice"
                ],
                "study_suggestions": [
                    "Create a regular study schedule for consistent practice",
                    "Focus on understanding concepts rather than memorization",
                    "Use the learning roadmap to track your progress",
                    "Challenge yourself gradually with harder difficulty levels"
                ],
                "motivation_message": "Success comes from consistent effort and persistence. You have everything it takes to achieve your goals!"
            }
        ]
        
        # Use student_id to consistently pick the same template
        template_index = abs(hash(str(student_id))) % len(feedback_templates)
        return feedback_templates[template_index]

# Global fast AI instance
fast_ai = FastAI()