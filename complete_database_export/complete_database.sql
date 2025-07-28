-- Complete Nura AI Database Export
-- Generated: Mon Jul 28 07:35:42 PM UTC 2025

 CREATE TABLE adaptive_quiz_sessions (id INTEGER NOT NULL, session_id VARCHAR(36) NOT NULL, student_id VARCHAR(36) NOT NULL, topic_id VARCHAR(36) NOT NULL, initial_difficulty VARCHAR(20) NOT NULL, current_difficulty VARCHAR(20) NOT NULL, total_sets INTEGER, current_set INTEGER, session_data JSON, final_proficiency_score DOUBLE PRECISION, is_completed BOOLEAN, start_time TIMESTAMP, end_time TIMESTAMP);
 CREATE TABLE admins (id INTEGER NOT NULL, admin_id VARCHAR(36) NOT NULL, user_id INTEGER NOT NULL, department VARCHAR(100), permissions JSON, last_login TIMESTAMP);
 CREATE TABLE performance_trends (id INTEGER NOT NULL, trend_id VARCHAR(36) NOT NULL, student_id VARCHAR(36) NOT NULL, topic_id VARCHAR(36) NOT NULL, proficiency_score DOUBLE PRECISION, trend_graph_data JSON, last_updated TIMESTAMP);
 CREATE TABLE question_sets (id INTEGER NOT NULL, question_set_id VARCHAR(36) NOT NULL, topic_id VARCHAR(36) NOT NULL, subject_id VARCHAR(36), difficulty_level VARCHAR(20) NOT NULL, question_ids JSON, min_questions INTEGER, max_questions INTEGER, success_threshold DOUBLE PRECISION, created_at TIMESTAMP, total_marks INTEGER);
 CREATE TABLE questions (id INTEGER NOT NULL, question_id VARCHAR(36) NOT NULL, set_id VARCHAR(36) NOT NULL, description TEXT NOT NULL, options JSON, correct_option VARCHAR(10) NOT NULL, marks_worth INTEGER, explanation TEXT, image_url VARCHAR(255));
 CREATE TABLE quiz_responses (id INTEGER NOT NULL, response_id VARCHAR(36) NOT NULL, quiz_id VARCHAR(36) NOT NULL, question_id VARCHAR(36) NOT NULL, selected_option VARCHAR(10), is_correct BOOLEAN, time_taken INTEGER, nura_feedback TEXT);
 CREATE TABLE quizzes (id INTEGER NOT NULL, quiz_id VARCHAR(36) NOT NULL, student_id VARCHAR(36) NOT NULL, topic_id VARCHAR(36) NOT NULL, question_set_id VARCHAR(36) NOT NULL, score DOUBLE PRECISION, total_marks INTEGER, date_taken TIMESTAMP, time_taken INTEGER);
 CREATE TABLE students (id INTEGER NOT NULL, student_id VARCHAR(36) NOT NULL, user_id INTEGER NOT NULL, grade_level VARCHAR(20) NOT NULL, preferred_subjects JSON);
 CREATE TABLE subjects (id INTEGER NOT NULL, subject_id VARCHAR(36) NOT NULL, name VARCHAR(100) NOT NULL, description TEXT);
 CREATE TABLE teachers (id INTEGER NOT NULL, teacher_id VARCHAR(36) NOT NULL, user_id INTEGER NOT NULL, school_name VARCHAR(200), subjects_taught JSON);
 CREATE TABLE topics (id INTEGER NOT NULL, topic_id VARCHAR(36) NOT NULL, subject_id VARCHAR(36) NOT NULL, name VARCHAR(100) NOT NULL, difficulty_level VARCHAR(20) NOT NULL);
 CREATE TABLE users (id INTEGER NOT NULL, user_id VARCHAR(36) NOT NULL, email VARCHAR(120) NOT NULL, password_hash VARCHAR(256) NOT NULL, full_name VARCHAR(100) NOT NULL, role VARCHAR(20) NOT NULL, created_at TIMESTAMP);


-- INSERT DATA

-- Data for users

-- Data for subjects

-- Data for topics

-- Data for question_sets

-- Data for questions

-- Data for quizzes

-- Data for quiz_responses

-- Data for students

-- Data for teachers

-- Data for admins

-- Data for performance_trends

-- Data for adaptive_quiz_sessions

-- Data for users
INSERT INTO users VALUES (1, 'eeffc698-be00-4eae-908e-0783379324e2', 'Azib.muz@gmail.com', 'scrypt:32768:8:1$lYDVp9VXVtqqTt9c$6777f031ed6e0e546fac183e7e205bbffe3633598172db924eb6d4240a1c48f6a42a0a6fbd0e1955dabfd6958699a8ab5380a7f5905fbd5f9879e8058a415f74', 'Azib', 'student', '2025-07-02 06:26:37.917383');
INSERT INTO users VALUES (3, 'ea6e19ea-7100-44ec-a1f1-66aa127686a5', 'teacher@example.com', 'scrypt:32768:8:1$3UP9D6uTad07yLoT$6bce71a3d0830cc1ab994195081dd9094c1ae52d030a4567435ab4e6f80c97b90e4ad578e037cb6762a2680d2e82daba70cf29a28f5760141f3602b43b8b6ac2', 'Teacher', 'teacher', '2025-07-02 06:38:19.801571');
INSERT INTO users VALUES (4, 'cb4b0798-4216-4238-8201-b38699fe2f5e', 'student@example.com', 'scrypt:32768:8:1$VxbPbWFHdANcZXO6$7554d8dacdaeddbe41df9dd486c0249e68cde2f1a1a2b45f2c6befd112691d35f2e2af3eca2b9b4946e45c6c1bc8ec64cfc9a9543d2b3cbed28fd249fe2fa4df', 'Student', 'student', '2025-07-02 06:39:49.399406');
INSERT INTO users VALUES (2, '11eea724-d584-4c6b-aa8e-55a794dcccf6', 'admin@nuraai.com', 'scrypt:32768:8:1$WYtMJBuMH012o2wl$66cf619408a243bcf03706d24b80896e3c36133094090e2a6695344105a4ff2d5d8b52f9a6010d1270469122dc50147903342571d8e68aa9cda226d4686e2511', 'Nura AI Admin', 'admin', '2025-07-02 06:34:06.193072');
INSERT INTO users VALUES (8, '6b1d9e00-5fcc-4c43-a111-6415ea717df1', 'student6@example.com', 'scrypt:32768:8:1$Vsr5Dg6ah8QAdPvI$7f019bd29dc699956bd7ab788b5650a9be92cdb58dba9d1ecfd388d05987f1a02f7f18735887b40b1a7cca84da29ffbe942fc6922f601758198bcbe930b719bf', 'James Bond', 'student', '2025-07-17 10:49:48.075046');

-- Data for subjects
INSERT INTO subjects VALUES (16, '550e8400-e29b-41d4-a716-446655440000', 'Automotive', 'Comprehensive automotive technology, mechanics, and safety principles');

-- Data for topics
INSERT INTO topics VALUES (35, 'automotive-body-001', '550e8400-e29b-41d4-a716-446655440000', 'Body', 'easy');
INSERT INTO topics VALUES (36, 'automotive-engine-001', '550e8400-e29b-41d4-a716-446655440000', 'Engine', 'easy');
INSERT INTO topics VALUES (37, 'automotive-hazmat-001', '550e8400-e29b-41d4-a716-446655440000', 'Hazardous Materials', 'medium');
INSERT INTO topics VALUES (38, 'automotive-maintenance-001', '550e8400-e29b-41d4-a716-446655440000', 'Maintenance', 'easy');

-- Data for question_sets
INSERT INTO question_sets VALUES (41, 'qs-automotive-body-001', 'automotive-body-001', '550e8400-e29b-41d4-a716-446655440000', 'easy', NULL, 5, 10, 70, NULL, 5);
INSERT INTO question_sets VALUES (42, 'qs-automotive-engine-001', 'automotive-engine-001', '550e8400-e29b-41d4-a716-446655440000', 'easy', NULL, 3, 5, 70, NULL, 3);
INSERT INTO question_sets VALUES (43, 'qs-automotive-hazmat-001', 'automotive-hazmat-001', '550e8400-e29b-41d4-a716-446655440000', 'medium', NULL, 4, 6, 70, NULL, 4);
INSERT INTO question_sets VALUES (44, 'qs-automotive-maintenance-001', 'automotive-maintenance-001', '550e8400-e29b-41d4-a716-446655440000', 'easy', NULL, 5, 8, 70, NULL, 5);

-- Data for questions
INSERT INTO questions VALUES (8309, 'q-auto-body-001', 'qs-automotive-body-001', 'Please identify where the headlight of the car is located.', '["A) A", "B) B", "C) C", "D) D"]', 'C', 1, 'The headlight is typically located at the front of the vehicle to provide illumination for driving in low-light conditions.', '/static/images/quiz/question1.png');
INSERT INTO questions VALUES (8310, 'q-auto-body-002', 'qs-automotive-body-001', 'Please identify where the hood of the car is located.', '["A) A", "B) B", "C) C", "D) D"]', 'A', 1, 'The hood is the hinged cover over the engine compartment at the front of the vehicle.', '/static/images/quiz/question2.png');
INSERT INTO questions VALUES (8311, 'q-auto-body-003', 'qs-automotive-body-001', 'Please identify where the door of the car is located.', '["A) A", "B) B", "C) C", "D) D"]', 'C', 1, 'The door provides access to the passenger compartment of the vehicle.', '/static/images/quiz/question3.png');
INSERT INTO questions VALUES (8312, 'q-auto-body-004', 'qs-automotive-body-001', 'Please identify where the taillight of the car is located.', '["A) A", "B) B", "C) C", "D) D"]', 'A', 1, 'The taillight is located at the rear of the vehicle to signal braking and turning to other drivers.', '/static/images/quiz/question4.png');
INSERT INTO questions VALUES (8313, 'q-auto-body-005', 'qs-automotive-body-001', 'Please identify where the window of the car is located.', '["A) A", "B) B", "C) C", "D) D"]', 'B', 1, 'The window is a transparent panel that allows visibility into and out of the vehicle.', '/static/images/quiz/question5.png');
INSERT INTO questions VALUES (8321, 'q-auto-maint-001', 'qs-automotive-maintenance-001', 'This is the process of removing and replacing old engine oil to keep the engine running smoothly. What is it called?', '["A) Coolant flush", "B) Tire rotation", "C) Oil change", "D) Engine tune-up"]', 'C', 1, 'An oil change involves draining old engine oil and replacing it with fresh oil to lubricate engine components and maintain performance.', NULL);
INSERT INTO questions VALUES (8322, 'q-auto-maint-002', 'qs-automotive-maintenance-001', 'This part is often replaced during a tune-up and helps regulate air entering the engine. Name it.', '["A) Radiator cap", "B) Air filter", "C) Spark plug", "D) Timing chain"]', 'B', 1, 'The air filter prevents dirt and debris from entering the engine while allowing clean air to flow in for combustion.', NULL);
INSERT INTO questions VALUES (8323, 'q-auto-maint-003', 'qs-automotive-maintenance-001', 'This belt drives multiple engine components like the alternator and power steering. What is it?', '["A) Timing belt", "B) Drive chain", "C) Serpentine belt", "D) Fan belt"]', 'C', 1, 'The serpentine belt is a single, continuous belt that drives multiple accessories including the alternator, power steering pump, and air conditioning compressor.', NULL);
INSERT INTO questions VALUES (8324, 'q-auto-maint-004', 'qs-automotive-maintenance-001', 'This service ensures your tires wear evenly and improves vehicle handling. What is it called?', '["A) Tire inflation", "B) Wheel alignment", "C) Brake inspection", "D) Suspension check"]', 'B', 1, 'Wheel alignment adjusts the angles of the wheels to ensure they are perpendicular to the ground and parallel to each other for even tire wear.', NULL);
INSERT INTO questions VALUES (8325, 'q-auto-maint-005', 'qs-automotive-maintenance-001', 'Name the component checked and topped up during maintenance to ensure the brakes function properly.', '["A) Transmission fluid", "B) Brake fluid", "C) Windshield washer fluid", "D) Engine oil"]', 'B', 1, 'Brake fluid is a hydraulic fluid that transfers force from the brake pedal to the brake pads, enabling the vehicle to stop safely.', NULL);
INSERT INTO questions VALUES (8314, 'q-auto-engine-001', 'qs-automotive-engine-001', 'Please identify where the Cylinder Head of the engine is located.', '["A) A", "B) B", "C) C", "D) D"]', 'A', 1, 'The cylinder head is located at the top of the engine block and contains the valves and sometimes the camshaft.', '/static/images/quiz/engine_question1.png');
INSERT INTO questions VALUES (8315, 'q-auto-engine-002', 'qs-automotive-engine-001', 'Please identify where the Fuel Pump of the engine is located.', '["A) A", "B) B", "C) C", "D) D"]', 'C', 1, 'The fuel pump supplies fuel from the tank to the engine and is typically located near the fuel tank or engine.', '/static/images/quiz/engine_question2.png');
INSERT INTO questions VALUES (8316, 'q-auto-engine-003', 'qs-automotive-engine-001', 'Please identify where the Crank Shaft of the engine is located.', '["A) A", "B) B", "C) C", "D) D"]', 'D', 1, 'The crankshaft is located at the bottom of the engine and converts the reciprocating motion of pistons into rotational motion.', '/static/images/quiz/engine_question3.png');
INSERT INTO questions VALUES (8317, 'q-auto-hazmat-001', 'qs-automotive-hazmat-001', 'This fluid is flammable and powers most combustion engines. What is it?', '["A) Antifreeze", "B) Engine oil", "C) Diesel exhaust fluid", "D) Gasoline (Petrol)"]', 'D', 1, 'Gasoline (petrol) is a highly flammable hydrocarbon fuel used to power internal combustion engines in most vehicles.', '/static/images/quiz/hazmat_question1.png');
INSERT INTO questions VALUES (8318, 'q-auto-hazmat-002', 'qs-automotive-hazmat-001', 'Which battery component is considered hazardous due to its acidic content and lead plates?', '["A) Nickel-metal hydride battery", "B) Lithium-ion battery", "C) Lead-acid battery", "D) Alkaline battery"]', 'C', 1, 'Lead-acid batteries contain sulfuric acid and lead plates, making them hazardous materials that require proper handling and disposal.', '/static/images/quiz/hazmat_question2.png');
INSERT INTO questions VALUES (8319, 'q-auto-hazmat-003', 'qs-automotive-hazmat-001', 'This fluid is toxic and used for engine cooling. It must be handled with care. Name it.', '["A) Windshield washer fluid", "B) Antifreeze (Coolant)", "C) Transmission fluid", "D) Brake fluid"]', 'B', 1, 'Antifreeze (coolant) contains ethylene glycol or propylene glycol, which can be toxic if ingested and requires careful handling.', '/static/images/quiz/hazmat_question3.png');
INSERT INTO questions VALUES (8320, 'q-auto-hazmat-004', 'qs-automotive-hazmat-001', 'This type of oil, once used and dirty, is considered hazardous waste. What is it?', '["A) Synthetic oil", "B) Crude oil", "C) Transmission oil", "D) Used motor oil"]', 'D', 1, 'Used motor oil becomes contaminated with metals and chemicals during use, making it hazardous waste that must be properly recycled.', '/static/images/quiz/hazmat_question4.jpg');

-- Data for quizzes
INSERT INTO quizzes VALUES (60, '74b69f05-ecbf-4867-b8ee-f0214db0ee4b', 'aa377081-f285-4349-a17a-43dc8c693c7a', 'automotive-hazmat-001', 'qs-automotive-hazmat-001', 100, 4, '2025-07-28 15:42:13.124611', NULL);
INSERT INTO quizzes VALUES (61, 'a6d2e7a0-bc48-45fa-a274-23f41fd1016d', 'aa377081-f285-4349-a17a-43dc8c693c7a', 'automotive-body-001', 'qs-automotive-body-001', 60, 5, '2025-07-28 17:15:41.193201', NULL);
INSERT INTO quizzes VALUES (62, '6397421d-0798-4285-9bef-6f9f91b4b3e6', 'aa377081-f285-4349-a17a-43dc8c693c7a', 'automotive-maintenance-001', 'qs-automotive-maintenance-001', 80, 5, '2025-07-28 17:17:34.940161', NULL);

-- Data for quiz_responses
INSERT INTO quiz_responses VALUES (204, '6f541a84-cc2b-485a-b62d-50cf9eefb500', '74b69f05-ecbf-4867-b8ee-f0214db0ee4b', 'q-auto-hazmat-001', 'D', 't', 30, NULL);
INSERT INTO quiz_responses VALUES (205, 'a7f515e5-679f-47cd-9285-c918f4c0032c', '74b69f05-ecbf-4867-b8ee-f0214db0ee4b', 'q-auto-hazmat-002', 'C', 't', 30, NULL);
INSERT INTO quiz_responses VALUES (206, 'ad701258-70cf-4b17-8ce6-60635b928c59', '74b69f05-ecbf-4867-b8ee-f0214db0ee4b', 'q-auto-hazmat-003', 'B', 't', 30, NULL);
INSERT INTO quiz_responses VALUES (207, 'ab11f7a2-3569-4708-b3a9-91683a6e1dfc', '74b69f05-ecbf-4867-b8ee-f0214db0ee4b', 'q-auto-hazmat-004', 'D', 't', 30, NULL);
INSERT INTO quiz_responses VALUES (208, '6033624d-d476-415f-b9dd-76fb5f2b52db', 'a6d2e7a0-bc48-45fa-a274-23f41fd1016d', 'q-auto-body-001', 'D', 'f', 30, NULL);
INSERT INTO quiz_responses VALUES (209, '4593e947-849b-4b2e-a1c7-83710291cc76', 'a6d2e7a0-bc48-45fa-a274-23f41fd1016d', 'q-auto-body-002', 'C', 'f', 30, NULL);
INSERT INTO quiz_responses VALUES (210, '8cfdd3a0-b317-4796-af2f-4c13a934139d', 'a6d2e7a0-bc48-45fa-a274-23f41fd1016d', 'q-auto-body-003', 'C', 't', 30, NULL);
INSERT INTO quiz_responses VALUES (211, '33ffc543-9206-4938-bd37-26ddddd2bce6', 'a6d2e7a0-bc48-45fa-a274-23f41fd1016d', 'q-auto-body-004', 'A', 't', 30, NULL);
INSERT INTO quiz_responses VALUES (212, 'e8643eba-7611-44af-aa43-7bfc9b3b1215', 'a6d2e7a0-bc48-45fa-a274-23f41fd1016d', 'q-auto-body-005', 'B', 't', 30, NULL);
INSERT INTO quiz_responses VALUES (213, '229d88db-25b3-4c4f-a7f9-6aa36211ae41', '6397421d-0798-4285-9bef-6f9f91b4b3e6', 'q-auto-maint-001', 'C', 't', 30, NULL);
INSERT INTO quiz_responses VALUES (214, '995737e4-7e5f-46de-b42b-3c6a67cf6b36', '6397421d-0798-4285-9bef-6f9f91b4b3e6', 'q-auto-maint-002', 'B', 't', 30, NULL);
INSERT INTO quiz_responses VALUES (215, 'd7d1b6b3-50c5-42e5-9c75-a0c158bb216c', '6397421d-0798-4285-9bef-6f9f91b4b3e6', 'q-auto-maint-003', 'A', 'f', 30, NULL);
INSERT INTO quiz_responses VALUES (216, 'bb741988-569b-4538-8d4d-c0352de7c5b1', '6397421d-0798-4285-9bef-6f9f91b4b3e6', 'q-auto-maint-004', 'B', 't', 30, NULL);
INSERT INTO quiz_responses VALUES (217, '48196026-0558-4b85-b92a-d8c1b57ecdd3', '6397421d-0798-4285-9bef-6f9f91b4b3e6', 'q-auto-maint-005', 'B', 't', 30, NULL);

-- Data for students
INSERT INTO students VALUES (1, '24320c69-860c-4ac4-9742-3e52281c8c0e', 1, 12, '["Mathematics"]');
INSERT INTO students VALUES (2, 'aa377081-f285-4349-a17a-43dc8c693c7a', 4, 12, '["Mathematics"]');

-- Data for teachers
INSERT INTO teachers VALUES (2, '53739a89-0c2f-4fee-9cfb-7ba11a5eded4', 3, 'Virtu Nera', '["Mathematics"]');

-- Data for admins
INSERT INTO admins VALUES (1, '309b6b22-35ec-40dc-8aae-ba7472adfb0b', 2, 'System Administration', '["full_access", "user_management", "system_monitoring", "data_export"]', NULL);

-- Data for performance_trends
INSERT INTO performance_trends VALUES (6, '9eddcb00-51c2-4a14-a0d7-92a77301efa3', 'aa377081-f285-4349-a17a-43dc8c693c7a', 'automotive-hazmat-001', 100, '"[100.0]"', '2025-07-28 15:42:13.275548');
INSERT INTO performance_trends VALUES (7, '0d6fbb1a-d207-4da9-b8b8-211e63e7be4d', 'aa377081-f285-4349-a17a-43dc8c693c7a', 'automotive-body-001', 60, '"[60.0]"', '2025-07-28 17:15:41.337455');
INSERT INTO performance_trends VALUES (8, '1e6a05e4-b07d-4315-92aa-4bb22c8b1021', 'aa377081-f285-4349-a17a-43dc8c693c7a', 'automotive-maintenance-001', 80, '"[80.0]"', '2025-07-28 17:17:35.081012');

-- Data for adaptive_quiz_sessions

