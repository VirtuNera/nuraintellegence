# Nura AI Complete Database Export

**Generated:** $(date)  
**Database:** PostgreSQL  
**Total Tables:** 12  
**Total Records:** 55

## Export Contents

### 1. CSV Files (Individual Tables)
- `adaptive_quiz_sessions.csv` - 0 records
- `admins.csv` - 1 record
- `performance_trends.csv` - 3 records  
- `question_sets.csv` - 4 records
- `questions.csv` - 17 records (automotive quiz questions with images)
- `quiz_responses.csv` - 14 records
- `quizzes.csv` - 3 records
- `students.csv` - 2 records
- `subjects.csv` - 1 record (Automotive)
- `teachers.csv` - 1 record
- `topics.csv` - 4 records (Body, Engine, Hazardous Materials, Maintenance)
- `users.csv` - 5 records

### 2. SQL Files
- `complete_database.sql` - Complete database recreation script with CREATE TABLE and INSERT statements

### 3. JSON Export
- `complete_database.json` - Complete database in JSON format for easy import/export

## Database Structure

### Core Tables
- **users** - User authentication and profiles
- **students** - Learner-specific data
- **teachers** - Educator-specific data  
- **admins** - Administrator accounts

### Content Tables
- **subjects** - Learning subjects (currently: Automotive)
- **topics** - Subject topics (Body, Engine, Hazardous Materials, Maintenance)
- **question_sets** - Quiz question collections
- **questions** - Individual quiz questions with images

### Activity Tables
- **quizzes** - Quiz sessions
- **quiz_responses** - Individual question responses
- **performance_trends** - Learning analytics
- **adaptive_quiz_sessions** - Adaptive learning sessions

## Automotive Content Summary
- **4 Topics:** Body (5 questions), Engine (3 questions), Hazardous Materials (4 questions), Maintenance (5 questions)
- **17 Total Questions** with visual learning materials
- **Images:** Engine diagrams and hazardous materials photos
- **Learning Focus:** Automotive safety, parts identification, and maintenance procedures

## Restore Instructions

### From CSV Files
```bash
# Create tables using your application's migration system
# Then import CSV files:
\copy users FROM 'users.csv' WITH CSV HEADER;
\copy subjects FROM 'subjects.csv' WITH CSV HEADER;
# ... repeat for all tables
```

### From SQL File
```bash
psql your_database < complete_database.sql
```

### From JSON File
Use your application's JSON import functionality or write a custom importer.

## Data Integrity Notes
- All user passwords are properly hashed
- UUIDs are used for external identifiers
- JSON fields contain proper quiz options and responses
- Image URLs reference `/static/images/quiz/` directory
- All foreign key relationships are maintained