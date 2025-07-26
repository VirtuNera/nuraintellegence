"""
Script to read and analyze the Excel file containing quiz datasets
"""

import pandas as pd
import json
import os
from app import app, db
from models import Subject, Topic, QuestionSet, Question

def analyze_excel_file():
    """Analyze the Excel file structure and content"""
    
    excel_file = "attached_assets/quiz_datasets_1752201722623.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return
    
    try:
        # Read all sheets from the Excel file
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        print(f"✅ Excel file loaded successfully!")
        print(f"📊 Number of sheets: {len(excel_data)}")
        
        # Display information about each sheet
        for sheet_name, df in excel_data.items():
            print(f"\n📋 Sheet: {sheet_name}")
            print(f"   Rows: {len(df)}")
            print(f"   Columns: {len(df.columns)}")
            print(f"   Column names: {list(df.columns)}")
            
            # Display first few rows to understand structure
            print(f"\n   First 3 rows:")
            print(df.head(3).to_string())
            
            # Check for any NaN values
            nan_count = df.isna().sum().sum()
            print(f"   Missing values: {nan_count}")
            
        return excel_data
    
    except Exception as e:
        print(f"❌ Error reading Excel file: {str(e)}")
        return None

def create_database_from_excel(excel_data):
    """Create database tables from Excel data"""
    
    if not excel_data:
        print("❌ No Excel data to process")
        return
    
    with app.app_context():
        try:
            print("\n🔄 Processing Excel data into database...")
            
            # Process each sheet
            for sheet_name, df in excel_data.items():
                print(f"\n📋 Processing sheet: {sheet_name}")
                
                # Determine subject and topic from sheet name or data
                subject_name = sheet_name if sheet_name else "General Knowledge"
                
                # Create or get subject
                subject = Subject.query.filter_by(name=subject_name).first()
                if not subject:
                    subject = Subject(
                        name=subject_name,
                        description=f"Questions from {sheet_name} dataset"
                    )
                    db.session.add(subject)
                    db.session.flush()
                    print(f"   ✅ Created subject: {subject_name}")
                
                # Create topic
                topic_name = f"{subject_name} Questions"
                topic = Topic.query.filter_by(name=topic_name, subject_id=subject.subject_id).first()
                if not topic:
                    topic = Topic(
                        subject_id=subject.subject_id,
                        name=topic_name,
                        difficulty_level="Medium"
                    )
                    db.session.add(topic)
                    db.session.flush()
                    print(f"   ✅ Created topic: {topic_name}")
                
                # Process questions based on the DataFrame structure
                questions_created = process_questions_from_dataframe(df, topic, subject)
                print(f"   ✅ Created {questions_created} questions")
            
            # Commit all changes
            db.session.commit()
            print("\n✅ Database update completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating database: {str(e)}")

def process_questions_from_dataframe(df, topic, subject):
    """Process questions from a DataFrame and create database entries"""
    
    # Common column name mappings
    column_mappings = {
        'question': ['question', 'Question', 'QUESTION', 'description', 'Description'],
        'option_a': ['option_a', 'Option A', 'A', 'choice_a', 'Choice A'],
        'option_b': ['option_b', 'Option B', 'B', 'choice_b', 'Choice B'],
        'option_c': ['option_c', 'Option C', 'C', 'choice_c', 'Choice C'],
        'option_d': ['option_d', 'Option D', 'D', 'choice_d', 'Choice D'],
        'correct_answer': ['correct_answer', 'Correct Answer', 'answer', 'Answer', 'correct'],
        'difficulty': ['difficulty', 'Difficulty', 'level', 'Level'],
        'explanation': ['explanation', 'Explanation', 'rationale', 'Rationale']
    }
    
    # Find actual column names in the DataFrame
    actual_columns = {}
    for key, possible_names in column_mappings.items():
        for name in possible_names:
            if name in df.columns:
                actual_columns[key] = name
                break
    
    print(f"   🔍 Found columns: {actual_columns}")
    
    # Group questions by difficulty level
    difficulties = ['Very Easy', 'Easy', 'Medium', 'Hard', 'Very Hard']
    
    # If no difficulty column, create one set with all questions
    if 'difficulty' not in actual_columns:
        difficulty_groups = {'Medium': df}
    else:
        difficulty_groups = {}
        for difficulty in difficulties:
            difficulty_df = df[df[actual_columns['difficulty']].str.contains(difficulty, case=False, na=False)]
            if len(difficulty_df) > 0:
                difficulty_groups[difficulty] = difficulty_df
    
    questions_created = 0
    
    for difficulty, questions_df in difficulty_groups.items():
        if len(questions_df) == 0:
            continue
            
        # Create question set for this difficulty
        question_set = QuestionSet(
            topic_id=topic.topic_id,
            subject_id=subject.subject_id,
            difficulty_level=difficulty,
            min_questions=min(5, len(questions_df)),
            max_questions=min(10, len(questions_df)),
            success_threshold=80.0
        )
        db.session.add(question_set)
        db.session.flush()
        
        print(f"     📦 Created question set for {difficulty} with {len(questions_df)} questions")
        
        # Process each question
        for index, row in questions_df.iterrows():
            try:
                # Extract question data
                question_text = str(row.get(actual_columns.get('question', ''), '')).strip()
                if not question_text or question_text == 'nan':
                    continue
                
                # Extract options
                options = []
                option_keys = ['option_a', 'option_b', 'option_c', 'option_d']
                for opt_key in option_keys:
                    if opt_key in actual_columns:
                        option_text = str(row.get(actual_columns[opt_key], '')).strip()
                        if option_text and option_text != 'nan':
                            options.append(option_text)
                
                # If no separate options, try to extract from question text
                if not options:
                    # Look for options in the question text itself
                    options = extract_options_from_text(question_text)
                
                # Extract correct answer
                correct_answer = str(row.get(actual_columns.get('correct_answer', ''), '')).strip()
                if not correct_answer or correct_answer == 'nan':
                    correct_answer = 'A'  # Default to A if not specified
                
                # Extract explanation
                explanation = str(row.get(actual_columns.get('explanation', ''), '')).strip()
                if explanation == 'nan':
                    explanation = ""
                
                # Create question
                question = Question(
                    set_id=question_set.question_set_id,
                    description=question_text,
                    options=options,
                    correct_option=correct_answer,
                    marks_worth=1,
                    explanation=explanation
                )
                db.session.add(question)
                questions_created += 1
                
            except Exception as e:
                print(f"     ❌ Error processing question {index}: {str(e)}")
                continue
    
    return questions_created

def extract_options_from_text(text):
    """Extract options from question text if they're embedded"""
    options = []
    
    # Look for patterns like A) option, B) option, etc.
    import re
    option_pattern = r'[A-D]\)[^A-D)]*(?=[A-D]\)|$)'
    matches = re.findall(option_pattern, text)
    
    for match in matches:
        option_text = match[2:].strip()  # Remove A), B), etc.
        if option_text:
            options.append(option_text)
    
    return options

if __name__ == "__main__":
    print("📊 Analyzing Excel file structure...")
    excel_data = analyze_excel_file()
    
    if excel_data:
        print("\n🔄 Creating database from Excel data...")
        create_database_from_excel(excel_data)