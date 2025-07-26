"""
Test script to verify PISA Math adaptive quiz system functionality
"""

from app import app, db
from models import User, Student, Subject, Topic, QuestionSet, Question, AdaptiveQuizSession
from adaptive_quiz_engine import AdaptiveQuizEngine
import json

def test_pisa_adaptive_quiz():
    """Test the PISA Math adaptive quiz system"""
    
    with app.app_context():
        # Find PISA Math topic
        pisa_subject = Subject.query.filter_by(name="PISA Mathematics").first()
        if not pisa_subject:
            print("❌ PISA Mathematics subject not found!")
            return
            
        pisa_topic = Topic.query.filter_by(subject_id=pisa_subject.subject_id).first()
        if not pisa_topic:
            print("❌ PISA Math topic not found!")
            return
            
        print(f"✅ Found PISA Math topic: {pisa_topic.name}")
        
        # Find test student
        test_student = Student.query.filter_by(student_id='aa377081-f285-4349-a17a-43dc8c693c7a').first()
        if not test_student:
            print("❌ Test student not found!")
            return
            
        print(f"✅ Found test student: {test_student.student_id}")
        
        # Test adaptive quiz engine
        adaptive_engine = AdaptiveQuizEngine()
        
        # Start an adaptive session
        session_result = adaptive_engine.start_adaptive_session(
            student_id=test_student.student_id,
            topic_id=pisa_topic.topic_id,
            initial_difficulty='Medium',
            total_sets=5
        )
        
        if session_result.get('success'):
            print(f"✅ Successfully started adaptive session: {session_result['session_id']}")
            print(f"   Initial difficulty: {session_result['current_difficulty']}")
            print(f"   Question set: {session_result['current_set']['set_number']}")
            
            # Display first question
            questions = session_result['current_set']['questions']
            if questions:
                first_question = questions[0]
                print(f"\n📝 Sample PISA Question:")
                print(f"   {first_question['description']}")
                print(f"   Options: {', '.join(first_question['options'])}")
                print(f"   Correct: {first_question.get('correct_option', 'N/A')}")
                
            # Test question set availability for all difficulty levels
            difficulties = ['Very Easy', 'Easy', 'Medium', 'Hard', 'Very Hard']
            for difficulty in difficulties:
                question_set = QuestionSet.query.filter_by(
                    topic_id=pisa_topic.topic_id,
                    difficulty_level=difficulty
                ).first()
                
                if question_set:
                    questions_count = Question.query.filter_by(set_id=question_set.question_set_id).count()
                    print(f"✅ {difficulty}: {questions_count} questions available")
                else:
                    print(f"❌ {difficulty}: No question set found")
                    
        else:
            print(f"❌ Failed to start adaptive session: {session_result.get('error')}")
            
        print(f"\n🎯 PISA Math adaptive quiz system test complete!")

if __name__ == "__main__":
    test_pisa_adaptive_quiz()