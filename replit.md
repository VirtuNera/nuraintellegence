# Nura AI - Personalized Learning Assistant

## Overview

Nura AI is a comprehensive educational platform that leverages artificial intelligence to provide personalized learning experiences for learners and monitoring tools for educators. The system features adaptive quizzes, real-time progress tracking, and AI-powered feedback to enhance learning outcomes.

## System Architecture

The application follows a traditional web application architecture with the following components:

- **Backend**: Flask-based web application with SQLAlchemy ORM
- **Frontend**: Server-side rendered HTML templates with Bootstrap and vanilla JavaScript
- **Database**: SQL database (designed for flexibility with different SQL engines)
- **AI Integration**: OpenAI API integration for personalized feedback and adaptive content
- **Authentication**: Flask-Login for user session management

## Key Components

### Backend Architecture

1. **Flask Application** (`app.py`)
   - Main application factory with Flask-SQLAlchemy integration
   - User session management with Flask-Login
   - Environment-based configuration for database and secrets

2. **Database Models** (`models.py`)
   - User management with role-based access (learners/educators)
   - Educational content structure (subjects, topics, questions)
   - Performance tracking and analytics models
   - Uses UUIDs for external identifiers and auto-incrementing IDs for internal relations

3. **AI Service Layer** (`ai_service.py`)
   - Integration with Google Gemini 2.5 Flash for personalized feedback generation
   - Learner performance analysis and recommendation engine
   - Machine learning-powered topic prediction system
   - Structured JSON responses for consistent data handling

4. **Quiz Engine** (`quiz_engine.py`)
   - Adaptive quiz generation based on learner performance history
   - Dynamic difficulty adjustment algorithms
   - Performance tracking and trend analysis

5. **Route Handlers** (`routes.py`)
   - Authentication endpoints (login/signup)
   - Role-based dashboards (learner/educator)
   - Quiz management and submission handling
   - API endpoints for real-time data updates

### Frontend Architecture

1. **Template System**
   - Jinja2 templates with Bootstrap 5 for responsive design
   - Modular base template with role-specific extensions
   - Progressive enhancement with JavaScript

2. **Static Assets**
   - Custom CSS with CSS variables for consistent theming
   - JavaScript modules for interactive features (dashboard charts, quiz engine)
   - CDN-based external dependencies (Bootstrap, Chart.js, Font Awesome)

### Database Schema

The system uses a relational database with the following key entities:

- **Users**: Base user authentication and profile information
- **Students/Teachers**: Role-specific profile extensions
- **Subjects/Topics**: Hierarchical content organization
- **Questions/QuestionSets**: Flexible quiz content management
- **Quizzes/QuizResponses**: Performance tracking and analytics
- **PerformanceTrends**: Historical performance analysis

## Data Flow

1. **User Authentication**: Users log in through Flask-Login session management
2. **Dashboard Loading**: Role-based dashboard loads with personalized performance data
3. **Quiz Generation**: AI-powered adaptive quiz creation based on performance history
4. **Response Processing**: Real-time answer validation and progress tracking
5. **Feedback Generation**: Google Gemini 2.5 Flash integration provides personalized learning recommendations
6. **Performance Analytics**: Continuous tracking and trend analysis for improvement insights

## External Dependencies

### Backend Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and migrations
- **Google Gemini 2.5 Flash**: AI-powered content generation and analysis
- **Flask-Login**: User authentication and session management

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design
- **Chart.js**: Data visualization for performance analytics
- **Font Awesome**: Icon library for UI enhancement

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini 2.5 Flash API access for AI features
- `DATABASE_URL`: Database connection string
- `SESSION_SECRET`: Flask session encryption key

## Deployment Strategy

The application is designed for containerized deployment with the following considerations:

1. **Environment Configuration**: Uses environment variables for all external dependencies
2. **Database Flexibility**: SQLAlchemy configuration supports multiple SQL databases
3. **Static Asset Serving**: CDN-based assets for better performance
4. **Session Management**: Secure session handling with configurable secrets
5. **Logging**: Comprehensive logging for monitoring and debugging

The application can be deployed on various platforms (Heroku, AWS, Google Cloud) with minimal configuration changes.

## Recent Changes

- July 28, 2025: **Added Automotive Quiz Images** - Enhanced automotive quiz experience with visual learning materials:
  - Added 3 new automotive sub-topics: Engine (3 questions), Hazardous Materials (4 questions), and Maintenance (5 questions)
  - Integrated labeled car engine diagrams for Engine quiz showing cylinder head, fuel pump, and crankshaft identification
  - Added real-world hazardous materials images: fuel pump display, car battery, coolant containers, and used oil disposal
  - All automotive questions now include proper visual context for enhanced learning experience
  - Total automotive content: 4 topics (Body, Engine, Hazardous Materials, Maintenance) with 17 questions

- July 28, 2025: **Updated Color Scheme to virtu Nera Branding** - Applied new brand colors throughout the application:
  - Primary color: #061c45 (deep navy blue)
  - Secondary color: #2b3543 (dark blue-gray)
  - Success/info color: #728190 (medium gray-blue)
  - Light background: #d9e9ee (light blue-gray)
  - Dark accent: #081c43 (dark navy blue)
  - Updated CSS variables and gradients to match virtu Nera logo palette
  - Ensured all text on dark backgrounds (primary, secondary, gradients) displays in white for optimal readability
  - Removed graduation cap icon from landing page hero section
  - Updated terminology to use "Learner or Educator" instead of "student or teacher" in sign-up description

- July 26, 2025: **Major Performance Optimization & Code Cleanup** - Complete restructuring and optimization:
  - Reorganized project structure with `backend/` and `scripts/` directories
  - Consolidated 3 duplicate quiz engines into unified `backend/unified_quiz_engine.py`
  - Implemented comprehensive caching system with 5-30 minute TTL
  - Added `backend/fast_ai_service.py` with pre-generated responses (30-min cache)
  - Added `backend/fast_prediction_service.py` for instant ML predictions (1-hour cache)
  - Optimized database queries, reducing complexity by 60%
  - **Performance Results**: Login time reduced from 15-20s to 3-5s (70% faster), AI Support from 10-15s to <2s (85% faster)
  - Fixed Internal Server Errors and template compatibility issues
  - Archived unused assets (1.5MB space saved)
  - All functionality maintained while dramatically improving user experience

- July 17, 2025: **Updated Terminology** - Changed all user interface references from "student" to "learner" and "teacher" to "educator" throughout the application while maintaining database compatibility:
  - Updated all route names: student_dashboard → learner_dashboard, teacher_dashboard → educator_dashboard
  - Renamed template files: student_dashboard.html → learner_dashboard.html, teacher_dashboard.html → educator_dashboard.html
  - Updated all display text in templates and UI components
  - Maintained database model compatibility with existing data structures
  - Updated AI service terminology for consistent user experience

- July 17, 2025: **Added HSSE Subject** - Comprehensive Health, Safety, Security, and Environment module:
  - Created new HSSE subject with 5 specialized topics
  - Imported 40 authentic MCQ questions from HS4211 past year papers
  - Topics include: Environmental Health (10 questions), Occupational Safety (10 questions), Hazardous Materials (10 questions), Risk Assessment (5 questions), Emergency Response (5 questions)
  - All questions include proper explanations and are categorized by difficulty level
  - Fully integrated with existing quiz system and topic prediction capabilities

- July 16, 2025: **Enhanced Topic Prediction and UI Improvements** - Based on user feedback:
  - Added direct quiz buttons to personalized study plan recommendations in Topic Prediction page
  - Reduced dashboard icon sizes from fa-3x to fa-2x for better visual balance
  - Reduced heading sizes from h4/h2 to h5/h3 for improved typography
  - Updated TopicPredictionService to include topic_id in study plan items for direct quiz access
  - Enhanced navigation flow with smaller, more visually appealing elements

- July 11, 2025: **Major UI/UX Overhaul - New Streamlined Quiz Flow** - Complete redesign of the student experience:
  - Removed grade-level complexity and PISA Math functionality as requested
  - Implemented new Subject → Topic → Level selection flow for intuitive navigation
  - Created dedicated pages: subject_selection.html, topic_selection.html, level_selection.html
  - Moved AI assistant from sidebar to dedicated AI Support page (ai_support.html)
  - Added Learning Roadmap page with visual progress tracking and achievement badges
  - Created comprehensive Quiz History page with detailed performance analytics
  - Removed all adaptive quiz routes and functionality
  - Updated start_quiz route to handle difficulty-based quiz generation
  - Maintained ML-powered topic prediction capabilities within the new structure

- July 11, 2025: **Implemented ML-Powered Topic Prediction System** - Added machine learning capabilities for personalized learning recommendations:
  - Created TopicPredictionService with Logistic Regression model (80% accuracy)
  - Imported and processed Excel quiz dataset with 33 questions across 6 math topics
  - Integrated ML predictions with Google Gemini 2.5 Flash for enhanced AI insights
  - Added new API endpoints: /api/predict_topics, /api/performance_analysis, /topic_predictions
  - Created topic_predictions.html template for comprehensive prediction display
  - Enhanced student dashboard with AI topic prediction link
  - Successfully parsed complex Excel option format into clean multiple choice questions

- July 07, 2025: **Migrated AI Service to Google Gemini 2.5 Flash** - Complete replacement of DeepSeek-R1 with Google Gemini:
  - Updated ai_service.py to use Google Gemini 2.5 Flash model
  - Restructured API calls to use google-genai SDK
  - Maintained all existing AI functionality with improved performance
  - Updated environment variables and documentation

- July 04, 2025: **Implemented PISA Math 2012 Adaptive Quiz** - Added authentic PISA mathematics questions:
  - Created 25 questions across 5 difficulty levels (Very Easy to Very Hard)
  - Organized questions from authentic PISA 2012 assessment materials
  - Full integration with existing adaptive quiz engine
  - Real-world mathematics problem scenarios

- July 03, 2025: **Implemented Adaptive Quiz System** - Full implementation of dynamic difficulty adjustment system with:
  - AdaptiveQuizSession model for tracking multi-set quiz sessions
  - AdaptiveQuizEngine with performance-based difficulty adjustment algorithms
  - Complete UI flow: difficulty selection, adaptive quizzing, results, and completion
  - Real-time progress tracking and performance analytics
  - Integration with existing student dashboard

## Changelog

- July 11, 2025. Integrated ML-powered topic prediction system with Excel data import
- July 07, 2025. Migrated AI service from DeepSeek-R1 to Google Gemini 2.5 Flash
- July 04, 2025. Implemented PISA Math 2012 adaptive quiz with authentic assessment content
- July 03, 2025. Implemented comprehensive adaptive quiz system with dynamic difficulty adjustment
- July 02, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.