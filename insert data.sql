INSERT INTO Admin (admin_id, admin_name, admin_email, admin_password, admin_phone) VALUES 
('AD01', 'Admin IT Society', 'it@staff.mmu.edu.my', 'AdminPass!01', '06-9977683' ),
('AD02', 'Admin Music Club', 'music@staff.mmu.edu.my', 'IloveMusic@99', '06-24342687'),
('AD03', 'Admin Volleyball Club', 'volleyball@staff.mmu.edu.my', 'Volley909', '06-9893345'),
('AD04', 'Admin Photography Club', 'photography@staff.mmu.edu.my', 'Photo$77', '06-2234578');

-- ORGANIZER (ID Format: ORxx)
INSERT INTO Organizer (organizer_id, organizer_name, organizer_email, organizer_password, organizer_phone) VALUES 
('OR01', 'IT Society', 'it.society@staff.mmu.edu.my', 'ItClub#2025', '011-3436769'),
('OR02', 'Music Club', 'music.club@staff.mmu.edu.my', 'DoReMi_123', '011-38788433'),
('OR03', 'Volleyball Club', 'volleyball.club@staff.mmu.edu.my', 'Goal!Keeper1', '011-98367443'),
('OR04', 'Photography Club', 'photo.club@staff.mmu.edu.my', 'Shutter_Click9', '011-8765789');

-- LECTURER (ID Format: LExx)
INSERT INTO Lecturer (lecturer_id, lecturer_name, lecturer_email, lecturer_password, lecturer_phone) VALUES 
('LE01', 'Dr. Tan Ah Kow', 'aktan@mmu.edu.my', 'TanLec*01', '012-63746544'),
('LE02', 'Madam Sarah Wong', 'swong@mmu.edu.my', 'Sarah#Teach2', '012-6373946'),
('LE03', 'Prof. Ahmad Zaki', 'azaki@mmu.edu.my', 'ProfZaki@33', '012-90384623'),
('LE04', 'Dr. Raj Kumar', 'rkumar@mmu.edu.my', 'Raj_Physics4', '012-9472638');

-- STUDENT (ID Format: STxx)
INSERT INTO Student (student_id, student_name, student_email, student_password, student_phone) VALUES 
('243UC245YH', 'Ali Bin Azmad', 'ali.bin.azmad@student.mmu.edu.my', 'Ali_123', '019-32764583'),
('243UC246T9', 'Lim Mei Ling', 'lim.mei.ling@student.mmu.edu.my', 'Mei_789', '019-74926499'),
('243UC245VH', 'Hau Lin Jun', 'hau.lin.jun@student.mmu.edu.my', 'limjun_12', '019-8364886'),
('243UC246H7', 'Ethan Yeo Zheng Ming', 'ethan.yeo.zheng@student.mmu.edu.my', 'yeoo456', '019-7364899');

INSERT INTO Rooms (room_name, capacity, location, room_type) VALUES 
('Grand Hall', 500, 'DTC', 'Hall'),
('Lecture Theatre 1', 150, 'FCI Building', 'Lecture Hall'),
('Computer Lab 3', 40, 'FCI Building', 'Lab'),
('Sports Field', 200, 'Football Stadium', 'Field');

INSERT INTO Equipments (item_name, total_stock) VALUES 
('Projector', 10),
('Microphone Stand', 15),
('PA System', 5),
('Whiteboard Markers', 50),
('Folding Chair', 200),
('Banquet Table', 50);

INSERT INTO Category (category_name, created_by_admin_id) VALUES 
('Academic', 'AD01'),       -- Created by Admin IT Society
('Entertainments', 'AD02'), -- Created by Admin Music Club
('Sports', 'AD03'),         -- Created by Admin Volleyball Club
('Others', 'AD04');         -- Created by Admin Photography Club


-- Event 1: Academic (by IT Society OR01)
INSERT INTO Event (title, description, start_datetime, end_datetime, event_status, venue_location, capacity, category_id, organizer_id) 
VALUES ('Python Bootcamp', 'Learn coding basics', '2026-03-01 09:00:00', '2026-03-01 18:00:00', 'Upcoming', 'Computer Lab 3', 40, 1, 'OR01');

-- Event 2: Sports (by Volleyball Club OR03)
INSERT INTO Event (title, description, start_datetime, end_datetime, event_status, venue_location, capacity, category_id, organizer_id) 
VALUES ('Inter-Uni Friendly', 'Friendly volleyball match', '2026-03-12 09:00:00', '2026-03-12 19:00:00', 'Upcoming', 'Sports Field', 200, 3, 'OR03');

-- Event 3: Entertainments (by Music Club OR02)
INSERT INTO Event (title, description, start_datetime, end_datetime, event_status, venue_location, capacity, category_id, organizer_id) 
VALUES ('Jazz Night', 'Live jazz performance', '2026-03-01 19:00:00', '2026-03-01 23:00:00', 'Upcoming', 'Grand Hall', 500, 2, 'OR02');

-- Event 4: Academic (by Lecturer Dr. Raj Kumar LE04)
INSERT INTO Event (title, description, start_datetime, end_datetime, event_status, venue_location, capacity, category_id, lecturer_id) 
VALUES ('Physics Future Talk', 'Discussion on Quantum Physics', '2026-02-15 08:00:00', '2026-02-15 14:00:00', 'Upcoming', 'Lecture Theatre 1', 150, 1, 'LE04');


-- 1. Approved booking for Python Bootcamp (Approved by Admin Volleyball AD03 for facilities)
INSERT INTO Booking (req_start_datetime, req_end_datetime, status_id, room_id, event_id, req_organizer_id, approved_by_admin_id) 
VALUES ('2025-06-10 08:00:00', '2025-06-10 14:00:00', 2, 3, 1, 'OR01', 'AD03');

-- 2. Approved booking for Volleyball Match (Approved by Admin Sports AD03)
INSERT INTO Booking (req_start_datetime, req_end_datetime, status_id, room_id, event_id, req_organizer_id, approved_by_admin_id) 
VALUES ('2025-06-12 16:00:00', '2025-06-12 20:00:00', 2, 4, 2, 'OR03', 'AD03');

-- 3. Pending booking for Jazz Night (Organizer OR02)
INSERT INTO Booking (req_start_datetime, req_end_datetime, status_id, room_id, event_id, req_organizer_id) 
VALUES ('2025-07-01 18:00:00', '2025-07-02 00:00:00', 1, 1, 3, 'OR02');

-- 4. Rejected booking for Physics Talk (Lecturer LE04, Rejected by Admin IT AD01)
INSERT INTO Booking (req_start_datetime, req_end_datetime, status_id, room_id, event_id, req_lecturer_id, approved_by_admin_id) 
VALUES ('2025-07-15 13:00:00', '2025-07-15 17:00:00', 3, 2, 4, 'LE04', 'AD01');


INSERT INTO Equipment_request (quantity, status_id, event_id, equipment_id, approved_by_admin_id) VALUES 
(1, 2, 1, 1, 'AD01'), -- Projector for Python (Approved)
(4, 2, 2, 4, 'AD03'), -- Markers for Volleyball (Approved)
(2, 1, 3, 2, NULL),   -- Mics for Jazz (Pending)
(1, 3, 4, 1, 'AD01'); -- Projector for Physics (Rejected)


INSERT INTO Registration (student_id, event_id, status) VALUES 
('243UC245YH', 1, 'Confirmed'), -- Ali joins Python
('243UC246T9', 1, 'Confirmed'), -- Mei Ling joins Python
('243UC245VH', 2, 'Confirmed'), -- Hau Lin Jun joins Volleyball
('243UC246H7', 3, 'Confirmed'); -- Ethan joins Jazz


INSERT INTO Announcements (title, message, target_audience, admin_id) VALUES 
('IT Week', 'Join us for coding week.', 'All', 'AD01'),
('Sports Carnival', 'Register for the annual carnival now!', 'Student', 'AD03'),
('Exam Regulations', 'Please read the new exam guidelines.', 'Student', 'AD01'),
('Photo Contest', 'Submit your best photos by Friday.', 'Organizer', 'AD04');


INSERT INTO Feedback (rating, comments, student_id, event_id) VALUES 
(5, 'Great workshop, learned a lot!', '243UC245YH', 1),
(4, 'Good game, but hot weather.', '243UC245VH', 2),
(5, 'Loved the music selection.', '243UC246H7', 3),
(3, 'Room was too cold.', '243UC246T9', 1);
