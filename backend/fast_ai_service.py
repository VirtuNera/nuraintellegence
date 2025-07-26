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
        """Generate fast, cached learner feedback"""
        # Use pre-generated responses for speed
        feedback_templates = [
            {
                "assessment": "You're making good progress! Keep practicing regularly.",
                "recommendations": ["Try quizzes in different subjects", "Focus on challenging topics"],
                "motivation": "Every question you answer makes you smarter!"
            },
            {
                "assessment": "Great effort! Your quiz performance shows dedication.",
                "recommendations": ["Review incorrect answers to learn", "Challenge yourself with harder topics"],
                "motivation": "Learning is a journey - you're doing great!"
            },
            {
                "assessment": "Nice work! You're building strong knowledge foundations.",
                "recommendations": ["Practice consistently", "Ask for help when needed"],
                "motivation": "Success comes from practice and persistence!"
            }
        ]
        
        # Use student_id to consistently pick the same template
        template_index = abs(hash(str(student_id))) % len(feedback_templates)
        return feedback_templates[template_index]

# Global fast AI instance
fast_ai = FastAI()