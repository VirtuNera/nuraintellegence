"""
PISA Mathematics 2012 - Adaptive Quiz System Data Initialization
Based on the PISA 2012 MCQ questions provided by the user
"""

from app import app, db
from models import Subject, Topic, QuestionSet, Question
import json

def init_pisa_math_data():
    """Initialize PISA Mathematics subject with all questions organized by difficulty"""
    
    with app.app_context():
        # Create PISA Mathematics subject
        pisa_math = Subject(
            name="PISA Mathematics",
            description="Programme for International Student Assessment - Mathematics Questions from 2012"
        )
        db.session.add(pisa_math)
        db.session.commit()
        
        # Create single topic for PISA Math
        pisa_topic = Topic(
            subject_id=pisa_math.subject_id,
            name="PISA Math 2012",
            difficulty_level="adaptive"
        )
        db.session.add(pisa_topic)
        db.session.commit()
        
        # Define all PISA questions with proper difficulty levels
        pisa_questions = [
            # Very Easy Level Questions (Basic comprehension)
            {
                'set_difficulty': 'Very Easy',
                'questions': [
                    {
                        'description': 'Memory Stick: Can Ivan transfer the 350 MB photo album by deleting at most two music albums?',
                        'options': ['Yes, by deleting Albums 1 and 8', 'Yes, by deleting Albums 2 and 4', 'No, there is not enough space', 'Yes, by deleting all albums'],
                        'correct_option': 'A',
                        'explanation': 'This requires basic calculation and understanding of memory allocation.'
                    },
                    {
                        'description': 'Ice-cream Shop: How much edging does Mari need for the counter?',
                        'options': ['3.5 m', '4.5 m', '5.5 m', '6.5 m'],
                        'correct_option': 'C',
                        'explanation': 'Basic perimeter calculation for the counter edge.'
                    },
                    {
                        'description': 'Apartment Purchase: Which set of measurements can estimate the total apartment floor area?',
                        'options': ['Measure all room dimensions separately', 'Measure four outer side lengths and calculate total area', 'Measure terrace only', 'Measure the bathroom only'],
                        'correct_option': 'B',
                        'explanation': 'Understanding area calculation methods for irregular shapes.'
                    },
                    {
                        'description': 'Sauce: How much oil is needed for 150 mL dressing?',
                        'options': ['60 mL', '75 mL', '90 mL', '120 mL'],
                        'correct_option': 'C',
                        'explanation': 'Basic proportion calculation for recipe scaling.'
                    },
                    {
                        'description': 'Garage: What is the total roof area?',
                        'options': ['15 m²', '25 m²', '30 m²', '35 m²'],
                        'correct_option': 'C',
                        'explanation': 'Basic area calculation for composite shapes.'
                    }
                ]
            },
            # Easy Level Questions
            {
                'set_difficulty': 'Easy',
                'questions': [
                    {
                        'description': 'Ice-cream Shop: What is the floor space area (excluding service area)?',
                        'options': ['25 m²', '31.5 m²', '40 m²', '50 m²'],
                        'correct_option': 'B',
                        'explanation': 'Area calculation excluding specific sections.'
                    },
                    {
                        'description': 'Ice-cream Shop: How many table sets fit in the seating area?',
                        'options': ['2', '3', '4', '5'],
                        'correct_option': 'C',
                        'explanation': 'Spatial reasoning and area allocation.'
                    },
                    {
                        'description': 'Oil Spill: What is the area of the oil spill?',
                        'options': ['1500 km²', '2200 km²', '2750 km²', '4000 km²'],
                        'correct_option': 'A',
                        'explanation': 'Area estimation from visual representation.'
                    },
                    {
                        'description': 'Drip Rate: What is the volume of infusion?',
                        'options': ['180 mL', '240 mL', '360 mL', '480 mL'],
                        'correct_option': 'C',
                        'explanation': 'Volume calculation based on rate and time.'
                    },
                    {
                        'description': 'Cable Television: Total households in Switzerland?',
                        'options': ['2.4 million', '2.9 million', '3.3 million', '3.8 million'],
                        'correct_option': 'C',
                        'explanation': 'Statistical interpretation and calculation.'
                    }
                ]
            },
            # Medium Level Questions
            {
                'set_difficulty': 'Medium',
                'questions': [
                    {
                        'description': 'Faulty Players: Is the tester\'s claim correct that more video players are sent for repair than audio players?',
                        'options': ['Yes, video players have a higher fault rate', 'No, because more audio players are made and more are faulty', 'Yes, because video players are more expensive', 'No, because no players are faulty'],
                        'correct_option': 'B',
                        'explanation': 'Statistical analysis requiring comparison of rates vs. absolute numbers.'
                    },
                    {
                        'description': 'Faulty Players: Which company has a lower overall percentage of faulty players?',
                        'options': ['Electrix Company', 'Tronics Company', 'Both are the same', 'Cannot be determined'],
                        'correct_option': 'A',
                        'explanation': 'Percentage calculation and comparison across different datasets.'
                    },
                    {
                        'description': 'Penguins: How many penguins are there after the first year?',
                        'options': ['8000', '10,000', '12,000', '14,000'],
                        'correct_option': 'C',
                        'explanation': 'Population growth calculation with given rate.'
                    },
                    {
                        'description': 'Drip Rate: What happens to D if n doubles?',
                        'options': ['It doubles', 'It halves', 'It stays the same', 'It increases by 50%'],
                        'correct_option': 'B',
                        'explanation': 'Understanding inverse relationships in mathematical formulas.'
                    },
                    {
                        'description': 'DVD Rental: Minimum DVDs to offset membership?',
                        'options': ['10', '12', '14', '15'],
                        'correct_option': 'C',
                        'explanation': 'Break-even analysis with cost comparison.'
                    }
                ]
            },
            # Hard Level Questions
            {
                'set_difficulty': 'Hard',
                'questions': [
                    {
                        'description': 'Power of the Wind: Why does the mayor\'s windmill arrangement not meet regulations?',
                        'options': ['The field is too small', 'Towers are too heavy', 'Distance is less than 200 m', 'There are too few turbines'],
                        'correct_option': 'C',
                        'explanation': 'Spatial analysis with regulatory constraints and geometric reasoning.'
                    },
                    {
                        'description': 'Power of the Wind: What is the maximum rotor blade tip speed?',
                        'options': ['150 km/h', '200 km/h', '300 km/h', '400 km/h'],
                        'correct_option': 'C',
                        'explanation': 'Complex calculation involving rotational speed and radius.'
                    },
                    {
                        'description': 'Sailing Ships: In how many years does the kite sail cost pay back?',
                        'options': ['5–6 years', '8–9 years', '12–13 years', 'Never pays back'],
                        'correct_option': 'B',
                        'explanation': 'Financial analysis with multiple variables and time value calculations.'
                    },
                    {
                        'description': 'Ferris Wheel: What is the height of point M?',
                        'options': ['60 m', '70 m', '80 m', '90 m'],
                        'correct_option': 'B',
                        'explanation': 'Trigonometric calculation involving circular motion and height.'
                    },
                    {
                        'description': 'Holiday Apartment: What is the expert\'s estimated value?',
                        'options': ['180,000 zeds', '190,000 zeds', '210,000 zeds', '220,000 zeds'],
                        'correct_option': 'C',
                        'explanation': 'Statistical inference and regression analysis for valuation.'
                    }
                ]
            },
            # Very Hard Level Questions
            {
                'set_difficulty': 'Very Hard',
                'questions': [
                    {
                        'description': 'Ferris Wheel: What is John\'s average speed for the round trip to the river and back?',
                        'options': ['18 km/h', '24 km/h', '28 km/h', '32 km/h'],
                        'correct_option': 'B',
                        'explanation': 'Complex average speed calculation with different speeds for each direction.'
                    },
                    {
                        'description': 'Climbing Mount Fuji: What is the latest start time to finish by 8 pm?',
                        'options': ['10 am', '11 am', 'Noon', '1 pm'],
                        'correct_option': 'B',
                        'explanation': 'Time calculation with variable climbing rates and elevation changes.'
                    },
                    {
                        'description': 'Climbing Mount Fuji: What is the average step length?',
                        'options': ['20 cm', '30 cm', '40 cm', '50 cm'],
                        'correct_option': 'C',
                        'explanation': 'Complex calculation involving distance, elevation, and step count.'
                    },
                    {
                        'description': 'DVD Rental: How much would Troy have paid as a non-member?',
                        'options': ['48 zeds', '52.50 zeds', '54.40 zeds', '60 zeds'],
                        'correct_option': 'C',
                        'explanation': 'Multi-step financial calculation with different pricing tiers.'
                    },
                    {
                        'description': 'Which Car: What is the extra tax for Alpha?',
                        'options': ['100 zeds', '110 zeds', '120 zeds', '130 zeds'],
                        'correct_option': 'B',
                        'explanation': 'Tax calculation based on multiple criteria and thresholds.'
                    }
                ]
            }
        ]
        
        # Create question sets for each difficulty level
        for difficulty_group in pisa_questions:
            difficulty = difficulty_group['set_difficulty']
            questions = difficulty_group['questions']
            
            # Create question set
            question_set = QuestionSet(
                topic_id=pisa_topic.topic_id,
                subject_id=pisa_math.subject_id,
                difficulty_level=difficulty,
                question_ids=[],
                min_questions=5,
                max_questions=5,
                success_threshold=80.0,
                total_marks=len(questions)
            )
            db.session.add(question_set)
            db.session.commit()
            
            # Create individual questions
            question_ids = []
            for i, q_data in enumerate(questions):
                question = Question(
                    set_id=question_set.question_set_id,
                    description=q_data['description'],
                    options=q_data['options'],
                    correct_option=q_data['correct_option'],
                    marks_worth=1,
                    explanation=q_data['explanation']
                )
                db.session.add(question)
                db.session.commit()
                question_ids.append(question.question_id)
            
            # Update question set with question IDs
            question_set.question_ids = question_ids
            db.session.commit()
            
            print(f"Created {difficulty} question set with {len(questions)} questions")
        
        print(f"\nPISA Mathematics 2012 adaptive quiz system initialized successfully!")
        print(f"Subject: {pisa_math.name}")
        print(f"Topic: {pisa_topic.name}")
        print(f"Total question sets: {len(pisa_questions)}")
        print(f"Difficulty levels: Very Easy, Easy, Medium, Hard, Very Hard")

if __name__ == "__main__":
    init_pisa_math_data()