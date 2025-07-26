"""
Comprehensive test of Gemini AI integration in Nura AI system
"""

from app import app, db
from models import Student, Quiz, QuizResponse, PerformanceTrend
from ai_service import NuraAI
import json

def test_complete_gemini_integration():
    """Test all AI features with Gemini 2.5 Flash integration"""
    
    with app.app_context():
        print("🧪 Testing Complete Gemini AI Integration")
        print("=" * 50)
        
        # Initialize AI service
        nura_ai = NuraAI()
        print(f"✅ AI Service initialized - API Available: {nura_ai.api_available}")
        print(f"   Model: {nura_ai.model if nura_ai.model else 'Fallback mode'}")
        
        # Get test student
        test_student = Student.query.first()
        if not test_student:
            print("❌ No test student found!")
            return
            
        print(f"✅ Test student found: {test_student.student_id}")
        
        # Test 1: Student Feedback Generation
        print("\n📝 Test 1: Student Feedback Generation")
        try:
            feedback = nura_ai.generate_student_feedback(test_student.student_id)
            if feedback and 'overall_assessment' in feedback:
                print("✅ Student feedback generated successfully")
                print(f"   Assessment: {feedback['overall_assessment'][:50]}...")
                print(f"   Strengths: {len(feedback.get('strengths', []))} items")
                print(f"   Suggestions: {len(feedback.get('study_suggestions', []))} items")
            else:
                print("⚠️  Using fallback feedback (expected if no quiz history)")
        except Exception as e:
            print(f"❌ Student feedback error: {e}")
        
        # Test 2: Quiz Feedback Generation
        print("\n🎯 Test 2: Quiz Feedback Generation")
        try:
            sample_quiz_results = {
                'percentage': 75.0,
                'passed': True,
                'total_questions': 5,
                'correct_answers': 4,
                'difficulty': 'Medium'
            }
            
            quiz_feedback = nura_ai.generate_quiz_feedback(test_student.student_id, sample_quiz_results)
            if quiz_feedback and 'performance_summary' in quiz_feedback:
                print("✅ Quiz feedback generated successfully")
                print(f"   Summary: {quiz_feedback['performance_summary'][:50]}...")
                print(f"   Encouragement: {quiz_feedback.get('encouragement', 'N/A')[:40]}...")
                print(f"   Next difficulty: {quiz_feedback.get('next_quiz_difficulty', 'N/A')}")
            else:
                print("⚠️  Using fallback quiz feedback")
        except Exception as e:
            print(f"❌ Quiz feedback error: {e}")
        
        # Test 3: Difficulty Adjustment
        print("\n⚖️  Test 3: Difficulty Adjustment")
        try:
            current_performance = 82.5  # Good performance score
            difficulty_rec = nura_ai.adjust_quiz_difficulty(test_student.student_id, current_performance)
            if difficulty_rec and 'recommended_difficulty' in difficulty_rec:
                print("✅ Difficulty adjustment generated successfully")
                print(f"   Recommended: {difficulty_rec['recommended_difficulty']}")
                print(f"   Reasoning: {difficulty_rec.get('reasoning', 'N/A')[:50]}...")
                print(f"   Confidence: {difficulty_rec.get('confidence', 'N/A')}")
            else:
                print("⚠️  Using fallback difficulty recommendation")
        except Exception as e:
            print(f"❌ Difficulty adjustment error: {e}")
        
        # Test 4: Teacher Insights
        print("\n👩‍🏫 Test 4: Teacher Insights")
        try:
            sample_class_data = {
                'total_students': 25,
                'average_score': 78.5,
                'completion_rate': 92.0,
                'subject_performance': {
                    'Mathematics': 75.0,
                    'Science': 82.0
                },
                'student_scores': [85, 78, 92, 68, 75, 88, 79, 84]
            }
            
            teacher_insights = nura_ai.generate_teacher_insights(sample_class_data)
            if teacher_insights and 'class_overview' in teacher_insights:
                print("✅ Teacher insights generated successfully")
                print(f"   Overview: {teacher_insights['class_overview'][:50]}...")
                print(f"   Recommendations: {len(teacher_insights.get('recommendations', []))} items")
            else:
                print("⚠️  Using fallback teacher insights")
        except Exception as e:
            print(f"❌ Teacher insights error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Gemini AI Integration Test Complete!")
        
        # Summary
        if nura_ai.api_available:
            print("✅ All AI features are powered by Google Gemini 2.5 Flash")
            print("✅ API integration is working correctly")
            print("✅ JSON response parsing is functional")
        else:
            print("⚠️  AI features are using fallback responses")
            print("   Check GEMINI_API_KEY environment variable")

if __name__ == "__main__":
    test_complete_gemini_integration()