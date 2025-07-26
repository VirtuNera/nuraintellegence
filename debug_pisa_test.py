"""
Debug test for PISA Math adaptive quiz system
"""

from app import app, db
from models import Student, Topic, QuestionSet, Question
from adaptive_quiz_engine import AdaptiveQuizEngine
import traceback

def debug_pisa_test():
    """Debug the PISA Math adaptive quiz system step by step"""
    
    with app.app_context():
        try:
            print("=== DEBUGGING PISA MATH ADAPTIVE QUIZ ===")
            
            # Step 1: Find PISA Math topic
            pisa_topic = Topic.query.filter_by(name='PISA Math 2012').first()
            print(f"1. PISA Topic found: {pisa_topic.topic_id if pisa_topic else 'NOT FOUND'}")
            
            # Step 2: Find test student
            test_student = Student.query.filter_by(student_id='aa377081-f285-4349-a17a-43dc8c693c7a').first()
            print(f"2. Test student found: {test_student.student_id if test_student else 'NOT FOUND'}")
            
            # Step 3: Check available question sets
            if pisa_topic:
                question_sets = QuestionSet.query.filter_by(topic_id=pisa_topic.topic_id).all()
                print(f"3. Available question sets: {len(question_sets)}")
                
                for qs in question_sets:
                    questions = Question.query.filter_by(set_id=qs.question_set_id).all()
                    print(f"   - {qs.difficulty_level}: {len(questions)} questions")
                
                # Step 4: Test specific difficulty level
                test_difficulty = 'Medium'
                medium_set = QuestionSet.query.filter_by(
                    topic_id=pisa_topic.topic_id,
                    difficulty_level=test_difficulty
                ).first()
                
                if medium_set:
                    print(f"4. {test_difficulty} question set found: {medium_set.question_set_id}")
                    questions = Question.query.filter_by(set_id=medium_set.question_set_id).all()
                    print(f"   Questions in set: {len(questions)}")
                    
                    if questions:
                        print(f"   Sample question: {questions[0].description[:50]}...")
                        print(f"   Options: {questions[0].options}")
                        
                        # Step 5: Test adaptive engine initialization
                        print("\n5. Testing adaptive engine...")
                        engine = AdaptiveQuizEngine()
                        
                        # Step 6: Test session creation
                        print("6. Testing session creation...")
                        result = engine.start_adaptive_session(
                            student_id=test_student.student_id,
                            topic_id=pisa_topic.topic_id,
                            initial_difficulty=test_difficulty,
                            total_sets=3
                        )
                        
                        if result:
                            print(f"   ✅ Session created successfully: {result.get('session_id')}")
                            print(f"   Current difficulty: {result.get('current_difficulty')}")
                            print(f"   Questions in first set: {len(result.get('current_set', {}).get('questions', []))}")
                        else:
                            print("   ❌ Session creation failed")
                            
                    else:
                        print("   ❌ No questions found in Medium set")
                else:
                    print(f"4. ❌ {test_difficulty} question set not found")
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            traceback.print_exc()
            
        print("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    debug_pisa_test()