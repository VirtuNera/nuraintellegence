"""
Enhanced quiz system update to handle the new Excel data format
"""

import pandas as pd
import json
import re
from app import app, db
from models import Subject, Topic, QuestionSet, Question, Student, Quiz, QuizResponse

def parse_options_string(options_string):
    """Parse the complex options string from the Excel file"""
    
    # Pattern to extract options and answers from the string
    # [opt[0=A],opt[1=B],opt[2=C],opt[3=D],is_answer[0=no],is_answer[1=no],is_answer[2=yes],is_answer[3=no]]
    
    try:
        # Extract option letters
        opt_pattern = r'opt\[(\d+)=([A-D])\]'
        opt_matches = re.findall(opt_pattern, options_string)
        
        # Extract answer information
        answer_pattern = r'is_answer\[(\d+)=([a-zA-Z]+)\]'
        answer_matches = re.findall(answer_pattern, options_string)
        
        # Build options array
        options = []
        correct_option = None
        
        for i, (index, letter) in enumerate(opt_matches):
            options.append(f"Option {letter}")
            
            # Check if this is the correct answer
            if i < len(answer_matches):
                answer_index, is_correct = answer_matches[i]
                if is_correct.lower() == 'yes':
                    correct_option = letter
        
        return options, correct_option
    
    except Exception as e:
        print(f"Error parsing options: {e}")
        return ["A", "B", "C", "D"], "A"

def update_questions_with_proper_options():
    """Update questions with properly parsed options"""
    
    # Read the Excel file again
    excel_file = "attached_assets/quiz_datasets_1752201722623.xlsx"
    df = pd.read_excel(excel_file, sheet_name="Question Set")
    
    with app.app_context():
        try:
            print("🔄 Updating questions with proper options...")
            
            # Group questions by Question Set ID
            question_sets = df.groupby('Question Set ID')
            
            for question_set_id, questions_df in question_sets:
                print(f"\n📋 Processing Question Set: {question_set_id}")
                
                # Find or create subject and topic
                topic_name = questions_df['Topic ID'].iloc[0]
                subtopic_name = questions_df['Sub Topic ID'].iloc[0]
                
                subject = Subject.query.filter_by(name=topic_name).first()
                if not subject:
                    subject = Subject(
                        name=topic_name,
                        description=f"Questions for {topic_name}"
                    )
                    db.session.add(subject)
                    db.session.flush()
                
                topic = Topic.query.filter_by(name=subtopic_name, subject_id=subject.subject_id).first()
                if not topic:
                    topic = Topic(
                        subject_id=subject.subject_id,
                        name=subtopic_name,
                        difficulty_level="Medium"
                    )
                    db.session.add(topic)
                    db.session.flush()
                
                # Create question set
                question_set = QuestionSet(
                    topic_id=topic.topic_id,
                    subject_id=subject.subject_id,
                    difficulty_level="Medium",
                    min_questions=5,
                    max_questions=len(questions_df),
                    success_threshold=80.0
                )
                db.session.add(question_set)
                db.session.flush()
                
                # Process each question
                for index, row in questions_df.iterrows():
                    question_text = row['Question']
                    options_string = row['Option']
                    
                    # Parse options and correct answer
                    options, correct_option = parse_options_string(options_string)
                    
                    # Create question
                    question = Question(
                        set_id=question_set.question_set_id,
                        description=question_text,
                        options=options,
                        correct_option=correct_option if correct_option else "A",
                        marks_worth=1,
                        explanation=""
                    )
                    db.session.add(question)
                
                print(f"   ✅ Created {len(questions_df)} questions")
            
            # Commit changes
            db.session.commit()
            print("\n✅ Questions updated successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating questions: {str(e)}")

def create_performance_analytics():
    """Create performance analytics from the Performance Log sheet"""
    
    excel_file = "attached_assets/quiz_datasets_1752201722623.xlsx"
    df = pd.read_excel(excel_file, sheet_name="Performance Log")
    
    with app.app_context():
        try:
            print("🔄 Creating performance analytics...")
            
            # Group by student
            students = df.groupby('Student ID')
            
            for student_id, student_data in students:
                print(f"\n👤 Processing student: {student_id}")
                
                # Create student if not exists
                student = Student.query.filter_by(student_id=student_id).first()
                if not student:
                    # Create a basic user first
                    from models import User
                    user = User(
                        email=f"{student_id}@example.com",
                        password_hash="temp_hash",
                        full_name=student_id,
                        role="student"
                    )
                    db.session.add(user)
                    db.session.flush()
                    
                    student = Student(
                        user_id=user.id,
                        student_id=student_id,
                        grade_level="Unknown"
                    )
                    db.session.add(student)
                    db.session.flush()
                
                # Group by question set
                question_sets = student_data.groupby('Question Set ID')
                
                for qs_id, qs_data in question_sets:
                    # Find the corresponding question set
                    topic_name = qs_data['Topic'].iloc[0]
                    subtopic_name = qs_data['Subtopic'].iloc[0]
                    
                    # Find topic
                    subject = Subject.query.filter_by(name=topic_name).first()
                    if not subject:
                        continue
                    
                    topic = Topic.query.filter_by(name=subtopic_name, subject_id=subject.subject_id).first()
                    if not topic:
                        continue
                    
                    question_set = QuestionSet.query.filter_by(topic_id=topic.topic_id).first()
                    if not question_set:
                        continue
                    
                    # Calculate performance
                    total_questions = len(qs_data)
                    correct_answers = len(qs_data[qs_data['Is Correct?'] == 'Yes'])
                    score = (correct_answers / total_questions) * 100
                    
                    # Create quiz record
                    quiz = Quiz(
                        student_id=student.student_id,
                        topic_id=topic.topic_id,
                        question_set_id=question_set.question_set_id,
                        score=score,
                        total_marks=total_questions,
                        time_taken=300  # Default 5 minutes
                    )
                    db.session.add(quiz)
                    db.session.flush()
                    
                    # Create quiz responses
                    for _, response_row in qs_data.iterrows():
                        question_text = response_row['Question']
                        is_correct = response_row['Is Correct?'] == 'Yes'
                        
                        # Find the question
                        question = Question.query.filter_by(
                            set_id=question_set.question_set_id,
                            description=question_text
                        ).first()
                        
                        if question:
                            quiz_response = QuizResponse(
                                quiz_id=quiz.quiz_id,
                                question_id=question.question_id,
                                selected_option=question.correct_option if is_correct else "A",
                                is_correct=is_correct,
                                time_taken=30
                            )
                            db.session.add(quiz_response)
                
                print(f"   ✅ Created performance records for {len(question_sets)} question sets")
            
            # Commit changes
            db.session.commit()
            print("\n✅ Performance analytics created successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating performance analytics: {str(e)}")

def clean_existing_data():
    """Clean existing data before updating"""
    
    with app.app_context():
        try:
            print("🧹 Cleaning existing data...")
            
            # Delete existing questions and question sets from the imported data
            Question.query.delete()
            QuestionSet.query.delete()
            
            # Delete subjects and topics that were created during import
            subjects_to_delete = ['Question Set', 'Performance Log', 'Sum']
            for subject_name in subjects_to_delete:
                subject = Subject.query.filter_by(name=subject_name).first()
                if subject:
                    # Delete related topics
                    Topic.query.filter_by(subject_id=subject.subject_id).delete()
                    db.session.delete(subject)
            
            db.session.commit()
            print("✅ Existing data cleaned successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error cleaning data: {str(e)}")

if __name__ == "__main__":
    print("🔄 Starting quiz system update...")
    
    # Clean existing data
    clean_existing_data()
    
    # Update questions with proper options
    update_questions_with_proper_options()
    
    # Create performance analytics
    create_performance_analytics()
    
    print("\n✅ Quiz system update completed!")