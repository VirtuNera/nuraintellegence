#!/bin/bash
# Nura AI Database Backup Script
# Created: July 28, 2025

echo "Starting database backup..."

# Create backup directory with timestamp
BACKUP_DIR="database_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Export all tables to CSV
echo "Exporting tables to CSV..."
psql $DATABASE_URL -c "\copy (SELECT * FROM users) TO '$BACKUP_DIR/users.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM subjects) TO '$BACKUP_DIR/subjects.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM topics) TO '$BACKUP_DIR/topics.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM question_sets) TO '$BACKUP_DIR/question_sets.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM questions) TO '$BACKUP_DIR/questions.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM quizzes) TO '$BACKUP_DIR/quizzes.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM quiz_responses) TO '$BACKUP_DIR/quiz_responses.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM students) TO '$BACKUP_DIR/students.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM teachers) TO '$BACKUP_DIR/teachers.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM admins) TO '$BACKUP_DIR/admins.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM performance_trends) TO '$BACKUP_DIR/performance_trends.csv' WITH CSV HEADER"
psql $DATABASE_URL -c "\copy (SELECT * FROM adaptive_quiz_sessions) TO '$BACKUP_DIR/adaptive_quiz_sessions.csv' WITH CSV HEADER"

# Export database schema
echo "Exporting database schema..."
psql $DATABASE_URL -c "\d+" > "$BACKUP_DIR/schema_info.txt"

# Create database statistics
echo "Creating database statistics..."
psql $DATABASE_URL -c "
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t 
WHERE table_schema = 'public' 
ORDER BY table_name;
" > "$BACKUP_DIR/table_stats.txt"

# Create backup info file
echo "Creating backup information..."
cat > "$BACKUP_DIR/backup_info.txt" << EOF
Nura AI Database Backup
Created: $(date)
Database: PostgreSQL
Backup Type: CSV Export + Schema
Tables Exported: 12

Files included:
- users.csv (User accounts and authentication)
- subjects.csv (Learning subjects)
- topics.csv (Subject topics)
- question_sets.csv (Quiz question sets)
- questions.csv (Quiz questions with images)
- quizzes.csv (Quiz sessions)
- quiz_responses.csv (Student responses)
- students.csv (Learner profiles)
- teachers.csv (Educator profiles)
- admins.csv (Administrator accounts)
- performance_trends.csv (Learning analytics)
- adaptive_quiz_sessions.csv (Adaptive learning sessions)
- schema_info.txt (Database structure)
- table_stats.txt (Table statistics)

To restore:
1. Create new PostgreSQL database
2. Run the database migration to create tables
3. Import CSV files using COPY commands or import tools
EOF

echo "Backup completed in: $BACKUP_DIR"
ls -la "$BACKUP_DIR"