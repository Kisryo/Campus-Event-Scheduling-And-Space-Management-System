CREATE TABLE RequestStatus (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    status_name VARCHAR(20) NOT NULL
);

INSERT INTO RequestStatus (status_id, status_name) VALUES 
(1, 'Pending'), (2, 'Approved'), (3, 'Rejected');

CREATE TABLE Admin (
    admin_id VARCHAR(20) PRIMARY KEY,  
    admin_name VARCHAR(100) NOT NULL,
    admin_email VARCHAR(100) UNIQUE NOT NULL,
    admin_password VARCHAR(255) NOT NULL,
    admin_phone VARCHAR(20),
    admin_account_status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE Organizer (
    organizer_id VARCHAR(20) PRIMARY KEY, 
    organizer_name VARCHAR(100) NOT NULL,
    organizer_email VARCHAR(100) UNIQUE NOT NULL,
    organizer_password VARCHAR(255) NOT NULL,
    organizer_phone VARCHAR(20),
    organizer_account_status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE Lecturer (
    lecturer_id VARCHAR(20) PRIMARY KEY, 
    lecturer_name VARCHAR(100) NOT NULL,
    lecturer_email VARCHAR(100) UNIQUE NOT NULL,
    lecturer_password VARCHAR(255) NOT NULL,
    lecturer_phone VARCHAR(20),
    lecturer_account_status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE Student (
    student_id VARCHAR(20) PRIMARY KEY, 
    student_name VARCHAR(100) NOT NULL,
    student_email VARCHAR(100) UNIQUE NOT NULL,
    student_password VARCHAR(255) NOT NULL,
    student_phone VARCHAR(20),
    student_account_status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE Rooms (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    room_name VARCHAR(50) NOT NULL,
    capacity INT,
    location VARCHAR(100),
    room_type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE Equipments (
    equipment_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(100) NOT NULL,
    total_stock INT DEFAULT 0
);

CREATE TABLE Category (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL,
    created_by_admin_id VARCHAR(20), 
    FOREIGN KEY (created_by_admin_id) REFERENCES Admin(admin_id)
);

CREATE TABLE Event (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event-img VARCHAR(255) NULL,
    start_datetime DATETIME,
    end_datetime DATETIME,
    event_status VARCHAR(20),
    venue_location VARCHAR(100),
    capacity INT,
    category_id INT,
    organizer_id VARCHAR(20), -- Changed to VARCHAR
    lecturer_id VARCHAR(20),  -- Changed to VARCHAR
    FOREIGN KEY (category_id) REFERENCES Category(category_id),
    FOREIGN KEY (organizer_id) REFERENCES Organizer(organizer_id),
    FOREIGN KEY (lecturer_id) REFERENCES Lecturer(lecturer_id)
);

CREATE TABLE Booking (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    req_start_datetime DATETIME,
    req_end_datetime DATETIME,
    status_id INT DEFAULT 1,
    room_id INT,
    event_id INT,
    req_organizer_id VARCHAR(20), 
    req_lecturer_id VARCHAR(20),  
    approved_by_admin_id VARCHAR(20), 
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id),
    FOREIGN KEY (event_id) REFERENCES Event(event_id),
    FOREIGN KEY (req_organizer_id) REFERENCES Organizer(organizer_id),
    FOREIGN KEY (req_lecturer_id) REFERENCES Lecturer(lecturer_id),
    FOREIGN KEY (approved_by_admin_id) REFERENCES Admin(admin_id),
    FOREIGN KEY (status_id) REFERENCES RequestStatus(status_id)
);

CREATE TABLE Equipment_request (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    quantity INT,
    status_id INT DEFAULT 1,
    event_id INT,
    equipment_id INT,
    approved_by_admin_id VARCHAR(20), 
    FOREIGN KEY (event_id) REFERENCES Event(event_id),
    FOREIGN KEY (equipment_id) REFERENCES Equipments(equipment_id),
    FOREIGN KEY (approved_by_admin_id) REFERENCES Admin(admin_id),
    FOREIGN KEY (status_id) REFERENCES RequestStatus(status_id)
);

CREATE TABLE Registration (
    registration_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Confirmed',
    student_id VARCHAR(20) NOT NULL, 
    event_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (event_id) REFERENCES Event(event_id)
);

CREATE TABLE Announcements (
    announcement_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200),
    message TEXT,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    target_audience VARCHAR(50),
    admin_id VARCHAR(20), 
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id)
);

CREATE TABLE Feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    student_id VARCHAR(20), 
    event_id INT,
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (event_id) REFERENCES Event(event_id)
);
