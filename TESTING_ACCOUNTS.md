# Nura AI - Testing Accounts

## Student Accounts

### Primary Student Account
- **Email**: student@example.com
- **Password**: password123
- **Grade Level**: Grade 10
- **Preferred Subjects**: Mathematics, Science, English

### Additional Student Accounts
- **Email**: student2@example.com
- **Password**: password123
- **Grade Level**: Grade 9
- **Preferred Subjects**: History, Science

## Teacher Accounts

### Primary Teacher Account
- **Email**: teacher@example.com
- **Password**: password123
- **School**: Example High School
- **Subjects Taught**: Mathematics, Physics, Chemistry

## Admin Accounts

### System Administrator Account
- **Email**: admin@nuraai.com
- **Password**: admin123
- **Department**: System Administration
- **Access Level**: Full system access with comprehensive analytics dashboard
- **Features**: User management, system monitoring, performance analytics, data export

## Usage Instructions

1. Navigate to the login page
2. Enter the email and password from the accounts above
3. Click "Login" to access the respective dashboard
4. Students will see the student dashboard with quiz options and performance analytics
5. Teachers will see the teacher dashboard with class overview and student management tools
6. Admins will see the comprehensive admin dashboard with system-wide analytics and metrics

## Database Information

The accounts are automatically created when running `database_init.py`. If you need to reset the database, simply run the initialization script again.

## Notes

- All accounts use the same password for simplicity during testing
- The database includes sample quiz data, subjects, and performance metrics
- AI features now work with DeepSeek-R1 API and provide fallback responses when API key is not provided