-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: event_space_management
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `admin_id` varchar(20) NOT NULL,
  `admin_name` varchar(100) NOT NULL,
  `admin_email` varchar(100) NOT NULL,
  `admin_password` varchar(255) NOT NULL,
  `admin_phone` varchar(20) DEFAULT NULL,
  `admin_account_status` varchar(20) DEFAULT 'Active',
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `admin_email` (`admin_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES ('AD01','Nasuha binti Azmin','nasuha@staff.mmu.edu.my','Nasuhha459','016-3985783','Active'),('AD02','Chai An Wen','anwen@staff.mmu.edu.my','Anwen8402','019-74957399','Active'),('AD03','Kavitha a/p Muthusamy','kavitha@staff.mmu.edu.my','kavitha555','010-4639823','Active'),('AD04','Tan Xue Yan','xueyan@staff.mmu.edu.my','xueeyyan11','012-98320383','Active');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `announcements`
--

DROP TABLE IF EXISTS `announcements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcements` (
  `announcement_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) DEFAULT NULL,
  `message` text,
  `sent_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `target_audience` varchar(50) DEFAULT NULL,
  `admin_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`announcement_id`),
  KEY `admin_id` (`admin_id`),
  CONSTRAINT `announcements_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`admin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcements`
--

LOCK TABLES `announcements` WRITE;
/*!40000 ALTER TABLE `announcements` DISABLE KEYS */;
INSERT INTO `announcements` VALUES (1,'IT Week','Join us for coding week.','2025-12-29 07:39:20','All','AD01'),(2,'Sports Carnival','Register for the annual carnival now!','2025-12-29 07:39:20','Student','AD03'),(3,'Exam Regulations','Please read the new exam guidelines.','2025-12-29 07:39:20','Student','AD01'),(4,'Photo Contest','Submit your best photos by Friday.','2025-12-29 07:39:20','Organizer','AD04'),(5,'Sign Up Form','Please sign up the form if you want to join the latest event that organized by it society','2026-01-08 18:32:11','Lecturer','AD02'),(7,'System Maintenance','The portal will be down for maintenance on Sunday 2AM-4AM.','2026-01-24 00:27:12','All','AD01'),(8,'New Event Registrations','Students can now register for new event via the portal.','2026-01-24 20:29:27','Student','AD03'),(12,'Personal data','Please send me your personal data for information changing.','2026-01-31 19:25:44','LE04','AD02');
/*!40000 ALTER TABLE `announcements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking`
--

DROP TABLE IF EXISTS `booking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking` (
  `booking_id` int NOT NULL AUTO_INCREMENT,
  `booking_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `req_start_datetime` datetime DEFAULT NULL,
  `req_end_datetime` datetime DEFAULT NULL,
  `status_id` int DEFAULT '1',
  `room_id` int DEFAULT NULL,
  `event_id` int DEFAULT NULL,
  `req_organizer_id` varchar(20) DEFAULT NULL,
  `req_lecturer_id` varchar(20) DEFAULT NULL,
  `approved_by_admin_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`booking_id`),
  KEY `room_id` (`room_id`),
  KEY `event_id` (`event_id`),
  KEY `req_organizer_id` (`req_organizer_id`),
  KEY `req_lecturer_id` (`req_lecturer_id`),
  KEY `approved_by_admin_id` (`approved_by_admin_id`),
  KEY `status_id` (`status_id`),
  CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`),
  CONSTRAINT `booking_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `event` (`event_id`),
  CONSTRAINT `booking_ibfk_3` FOREIGN KEY (`req_organizer_id`) REFERENCES `organizer` (`organizer_id`),
  CONSTRAINT `booking_ibfk_4` FOREIGN KEY (`req_lecturer_id`) REFERENCES `lecturer` (`lecturer_id`),
  CONSTRAINT `booking_ibfk_5` FOREIGN KEY (`approved_by_admin_id`) REFERENCES `admin` (`admin_id`),
  CONSTRAINT `booking_ibfk_6` FOREIGN KEY (`status_id`) REFERENCES `requeststatus` (`status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking`
--

LOCK TABLES `booking` WRITE;
/*!40000 ALTER TABLE `booking` DISABLE KEYS */;
INSERT INTO `booking` VALUES (1,'2025-12-29 07:39:20','2025-06-10 08:00:00','2025-06-10 14:00:00',2,3,1,NULL,NULL,'AD03'),(2,'2025-12-29 07:39:20','2025-06-12 16:00:00','2025-06-12 20:00:00',2,4,2,'OR03',NULL,'AD03'),(3,'2025-12-29 07:39:20','2025-07-01 18:00:00','2025-07-02 00:00:00',3,1,3,NULL,NULL,NULL),(4,'2025-12-29 07:39:20','2025-07-15 13:00:00','2025-07-15 17:00:00',3,2,4,NULL,'LE04','AD01'),(5,'2026-01-07 08:57:40','2026-01-01 08:56:00','2026-01-03 00:00:00',2,1,5,NULL,NULL,'AD02'),(6,'2026-01-11 14:32:16','2026-03-04 07:00:00','2026-03-04 19:00:00',3,2,6,'OR04',NULL,NULL),(7,'2026-01-11 14:36:11','2026-03-01 19:00:00','2026-03-01 23:00:00',2,2,3,NULL,NULL,NULL),(8,'2026-01-11 16:11:11','2026-03-04 07:00:00','2026-03-04 19:00:00',2,1,6,'OR04',NULL,'AD02'),(10,'2026-01-12 13:15:13','2026-02-15 08:00:00','2026-02-15 14:00:00',2,2,4,NULL,'LE04','AD04'),(22,'2026-01-10 10:00:00','2026-03-20 10:00:00','2026-03-20 13:00:00',2,11,10,NULL,'LE03','AD01'),(23,'2026-01-12 15:45:00','2026-03-25 14:00:00','2026-03-25 17:00:00',2,12,11,'OR06',NULL,'AD04'),(24,'2026-01-18 10:00:00','2026-04-01 07:00:00','2026-04-01 11:00:00',2,4,12,'OR12',NULL,'AD03'),(25,'2026-01-20 09:00:00','2026-04-05 09:00:00','2026-04-05 21:00:00',2,6,13,'OR09',NULL,NULL),(28,'2026-01-31 16:55:43','2026-03-18 10:00:00','2026-03-18 22:00:00',2,12,16,'OR08',NULL,'AD02');
/*!40000 ALTER TABLE `booking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `category_name` varchar(50) NOT NULL,
  `created_by_admin_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`category_id`),
  KEY `created_by_admin_id` (`created_by_admin_id`),
  CONSTRAINT `category_ibfk_1` FOREIGN KEY (`created_by_admin_id`) REFERENCES `admin` (`admin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES (1,'Academic','AD01'),(2,'Entertainments','AD02'),(3,'Sports','AD03'),(7,'Seminar/workshop','AD02');
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipment_request`
--

DROP TABLE IF EXISTS `equipment_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment_request` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `quantity` int DEFAULT NULL,
  `status_id` int DEFAULT '1',
  `event_id` int DEFAULT NULL,
  `equipment_id` int DEFAULT NULL,
  `approved_by_admin_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`request_id`),
  KEY `event_id` (`event_id`),
  KEY `equipment_id` (`equipment_id`),
  KEY `approved_by_admin_id` (`approved_by_admin_id`),
  KEY `status_id` (`status_id`),
  CONSTRAINT `equipment_request_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `event` (`event_id`),
  CONSTRAINT `equipment_request_ibfk_2` FOREIGN KEY (`equipment_id`) REFERENCES `equipments` (`equipment_id`),
  CONSTRAINT `equipment_request_ibfk_3` FOREIGN KEY (`approved_by_admin_id`) REFERENCES `admin` (`admin_id`),
  CONSTRAINT `equipment_request_ibfk_4` FOREIGN KEY (`status_id`) REFERENCES `requeststatus` (`status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipment_request`
--

LOCK TABLES `equipment_request` WRITE;
/*!40000 ALTER TABLE `equipment_request` DISABLE KEYS */;
INSERT INTO `equipment_request` VALUES (1,1,2,1,1,'AD01'),(2,4,2,2,4,'AD03'),(3,2,2,3,2,NULL),(4,1,3,4,1,'AD01'),(5,1,1,3,1,NULL),(6,7,2,5,4,NULL),(7,20,1,6,5,NULL),(9,20,1,11,10,NULL),(10,1,1,11,12,NULL);
/*!40000 ALTER TABLE `equipment_request` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipments`
--

DROP TABLE IF EXISTS `equipments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipments` (
  `equipment_id` int NOT NULL AUTO_INCREMENT,
  `item_name` varchar(100) NOT NULL,
  `total_stock` int DEFAULT '0',
  PRIMARY KEY (`equipment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipments`
--

LOCK TABLES `equipments` WRITE;
/*!40000 ALTER TABLE `equipments` DISABLE KEYS */;
INSERT INTO `equipments` VALUES (1,'Projector',10),(2,'Microphone Stand',15),(3,'PA System',5),(4,'Whiteboard Markers',50),(5,'Folding Chair',110),(6,'Banquet Table',30),(7,'Extension Cord',55),(8,'Laptop',50),(9,'Chair',200),(10,'Table',100),(11,'Stage Light',10),(12,'Camera',30);
/*!40000 ALTER TABLE `equipments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `description` text,
  `event_img` varchar(255) DEFAULT NULL,
  `start_datetime` datetime DEFAULT NULL,
  `end_datetime` datetime DEFAULT NULL,
  `event_status` varchar(20) DEFAULT NULL,
  `venue_location` varchar(100) DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `organizer_id` varchar(20) DEFAULT NULL,
  `lecturer_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `category_id` (`category_id`),
  KEY `organizer_id` (`organizer_id`),
  KEY `lecturer_id` (`lecturer_id`),
  CONSTRAINT `event_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `category` (`category_id`),
  CONSTRAINT `event_ibfk_2` FOREIGN KEY (`organizer_id`) REFERENCES `organizer` (`organizer_id`),
  CONSTRAINT `event_ibfk_3` FOREIGN KEY (`lecturer_id`) REFERENCES `lecturer` (`lecturer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event`
--

LOCK TABLES `event` WRITE;
/*!40000 ALTER TABLE `event` DISABLE KEYS */;
INSERT INTO `event` VALUES (1,'Python Bootcamp','Learn coding basics','A001.jpg','2026-03-01 09:00:00','2026-03-01 18:00:00','Upcoming','Computer Lab 3',40,1,'OR01',NULL),(2,'Inter-Uni Friendly','Friendly volleyball match','A002.jpg','2026-03-12 09:00:00','2026-03-12 19:00:00','Upcoming','Sports Field',200,3,'OR03',NULL),(3,'Jazz Night','Live jazz performance','A003.jpg','2026-03-01 19:00:00','2026-03-01 23:00:00','Upcoming','Pending Approval',500,2,'OR02',NULL),(4,'Physics Future Talk','Discussion on Quantum Physics','A004.jpg','2026-02-15 08:00:00','2026-02-15 14:00:00','Upcoming','Lecture Theatre 1',150,7,NULL,'LE04'),(5,'Let\'s sing','Come join us if you have a wonderful voice','A005.jpg','2026-01-01 08:56:00','2026-01-03 00:00:00','Expired','Grand Hall',80,2,'OR02',NULL),(6,'Photography Day','In this event, I will show u how to take a really good picture.','A006.jpg','2026-03-04 07:00:00','2026-03-04 19:00:00','Upcoming','Grand Hall',20,2,'OR04',NULL),(10,'Advanced AI Research Seminar','A deep dive into neural networks by Prof. Ahmad Zaki.','A007.jpg','2026-03-20 10:00:00','2026-03-20 13:00:00','Upcoming','Seminar Room 1',50,7,NULL,'LE03'),(11,'Chinese Calligraphy Workshop','Learn the art of traditional brush writing.','A008.jpg','2026-03-25 14:00:00','2026-03-25 17:00:00','Upcoming','Activity Room',30,1,'OR06',NULL),(12,'Cyberjaya Fun Run','5km run around the campus perimeter.','A009.jpg','2026-04-01 07:00:00','2026-04-01 11:00:00','Upcoming','Sports Field',200,3,'OR12',NULL),(13,'Valorant Campus Championship','Inter-faculty e-sports tournament finals.','A010.jpg','2026-04-05 09:00:00','2026-04-05 21:00:00','Upcoming','Lecture Theatre 2',100,2,'OR09',NULL),(16,'dsfsjdfnl','gjggffghhgh',NULL,'2026-03-18 10:00:00','2026-03-18 22:00:00','Pending','Activity Room',50,2,'OR08',NULL);
/*!40000 ALTER TABLE `event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `feedback_id` int NOT NULL AUTO_INCREMENT,
  `rating` int DEFAULT NULL,
  `comments` text,
  `submitted_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `student_id` varchar(20) DEFAULT NULL,
  `event_id` int DEFAULT NULL,
  PRIMARY KEY (`feedback_id`),
  KEY `student_id` (`student_id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`),
  CONSTRAINT `feedback_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `event` (`event_id`),
  CONSTRAINT `feedback_chk_1` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
INSERT INTO `feedback` VALUES (9,5,'Love the music vibe!','2026-01-25 17:49:26','243UC245VH',5);
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lecturer`
--

DROP TABLE IF EXISTS `lecturer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lecturer` (
  `lecturer_id` varchar(20) NOT NULL,
  `lecturer_name` varchar(100) NOT NULL,
  `lecturer_email` varchar(100) NOT NULL,
  `lecturer_password` varchar(255) NOT NULL,
  `lecturer_phone` varchar(20) DEFAULT NULL,
  `lecturer_account_status` varchar(20) DEFAULT 'Active',
  PRIMARY KEY (`lecturer_id`),
  UNIQUE KEY `lecturer_email` (`lecturer_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lecturer`
--

LOCK TABLES `lecturer` WRITE;
/*!40000 ALTER TABLE `lecturer` DISABLE KEYS */;
INSERT INTO `lecturer` VALUES ('LE01','Dr. Tan Ah Kow','aktan@mmu.edu.my','TanLec*01','012-63746544','Active'),('LE02','Madam Sarah Wong','swong@mmu.edu.my','Sarah#Teach2','012-6373946','Active'),('LE03','Prof. Ahmad Zaki','azaki@mmu.edu.my','ProfZaki@33','012-90384623','Active'),('LE04','Dr. Raj Kumar','rkumar@mmu.edu.my','Raj_Physics4','012-9472638','Active'),('LE05','Ms. Lim Xue Lee','xuelee@mmu.edu.my','xuelee45','011-5682635','Active'),('LE06','Dr. Siti Aminah','siti.aminah@mmu.edu.my','SitiPass1','012-1231234','Active'),('LE07','Mr. John Doe','john.doe@mmu.edu.my','JohnDoe123','013-2342345','Active'),('LE08','Prof. Michael Chen','m.chen@mmu.edu.my','ChenMike9','014-3453456','Active'),('LE09','Dr. Jessica Leong','j.leong@mmu.edu.my','JessL88','015-4564567','Active'),('LE10','Mr. Azlan Shah','azlan.s@mmu.edu.my','Azlan!Shah','016-5675678','Active'),('LE11','Madam Deepa','deepa.r@mmu.edu.my','DeepaRe3','017-6786789','Active'),('LE12','Dr. Ng Wei Wei','ww.ng@mmu.edu.my','NgWeiWei0','018-7897890','Active');
/*!40000 ALTER TABLE `lecturer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `organizer`
--

DROP TABLE IF EXISTS `organizer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organizer` (
  `organizer_id` varchar(20) NOT NULL,
  `organizer_name` varchar(100) NOT NULL,
  `organizer_email` varchar(100) NOT NULL,
  `organizer_password` varchar(255) NOT NULL,
  `organizer_phone` varchar(20) DEFAULT NULL,
  `organizer_account_status` varchar(20) DEFAULT 'Active',
  PRIMARY KEY (`organizer_id`),
  UNIQUE KEY `organizer_email` (`organizer_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `organizer`
--

LOCK TABLES `organizer` WRITE;
/*!40000 ALTER TABLE `organizer` DISABLE KEYS */;
INSERT INTO `organizer` VALUES ('OR01','IT Society','it.society@mmu.edu.my','it123','011-3436769','Active'),('OR02','Music Club','music.club@mmu.edu.my','Music123','011-38788433','Active'),('OR03','Volleyball Club','volleyball.club@mmu.edu.my','Goal!Keeper1','011-98367443','Active'),('OR04','Photography Club','photo.club@mmu.edu.my','Shutter_Click9','011-8765789','Active'),('OR05','Debate Society','debate.society@mmu.edu.my','Debate#2026','012-1112223','Active'),('OR06','Chinese Cultural Society','chinese.society@mmu.edu.my','CCS_mmu1','013-2223334','Active'),('OR07','Indian Cultural Society','indian.society@mmu.edu.my','ICS_mmu1','014-3334445','Active'),('OR08','Japanese Culture Club','japanese.club@mmu.edu.my','Nihongo!','015-4445556','Active'),('OR09','E-Sports Club','esports.club@mmu.edu.my','GameOn123','016-5556667','Active'),('OR10','Cybersecurity Club','cybersecure.club@mmu.edu.my','HackerMan0','017-6667778','Active'),('OR11','Swimming Club','swimming.club@mmu.edu.my','Splash22','018-7778889','Active'),('OR12','Running Club','running.club@mmu.edu.my','FastLegs99','019-8889990','Active');
/*!40000 ALTER TABLE `organizer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration`
--

DROP TABLE IF EXISTS `registration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration` (
  `registration_id` int NOT NULL AUTO_INCREMENT,
  `registration_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(20) DEFAULT 'Confirmed',
  `student_id` varchar(20) NOT NULL,
  `event_id` int NOT NULL,
  PRIMARY KEY (`registration_id`),
  KEY `student_id` (`student_id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `registration_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`),
  CONSTRAINT `registration_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `event` (`event_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration`
--

LOCK TABLES `registration` WRITE;
/*!40000 ALTER TABLE `registration` DISABLE KEYS */;
INSERT INTO `registration` VALUES (1,'2025-12-29 07:39:20','Confirmed','243UC245YH',1),(2,'2025-12-29 07:39:20','Confirmed','243UC246T9',1),(4,'2025-12-29 07:39:20','Confirmed','243UC246H7',3),(7,'2026-01-07 03:42:03','Confirmed','243UC245VH',5),(8,'2026-01-10 17:58:35','Confirmed','243UC245VH',4),(9,'2026-01-21 15:37:22','Confirmed','243UC246Y9',6),(10,'2026-01-24 19:10:32','Confirmed','243UC245YH',12),(12,'2026-01-29 12:47:28','Confirmed','1221100003',13),(13,'2026-01-31 23:45:33','Confirmed','243UC247G7',2);
/*!40000 ALTER TABLE `registration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `requeststatus`
--

DROP TABLE IF EXISTS `requeststatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `requeststatus` (
  `status_id` int NOT NULL AUTO_INCREMENT,
  `status_name` varchar(20) NOT NULL,
  PRIMARY KEY (`status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `requeststatus`
--

LOCK TABLES `requeststatus` WRITE;
/*!40000 ALTER TABLE `requeststatus` DISABLE KEYS */;
INSERT INTO `requeststatus` VALUES (1,'Pending'),(2,'Approved'),(3,'Rejected');
/*!40000 ALTER TABLE `requeststatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rooms` (
  `room_id` int NOT NULL AUTO_INCREMENT,
  `room_name` varchar(50) NOT NULL,
  `capacity` int DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `room_type` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`room_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rooms`
--

LOCK TABLES `rooms` WRITE;
/*!40000 ALTER TABLE `rooms` DISABLE KEYS */;
INSERT INTO `rooms` VALUES (1,'Grand Hall',400,'DTC','Hall',1),(2,'Lecture Theatre 1',150,'FCI Building','Lecture Hall',1),(3,'Computer Lab 3',40,'FCI Building','Lab',1),(4,'Sports Field',200,'Football Stadium','Field',1),(6,'Lecture Theatre 2',150,'FOE','Lecture Hall',1),(7,'Computer Lab 1',40,'FCI','Lab',1),(8,'Computer Lab 2',40,'FCI','Lab',1),(9,'Meeting Room A',20,'Admin Block','Meeting Room',1),(10,'Badminton Court',30,'Sports Complex','Court',1),(11,'Seminar Room 1',50,'FOM','Seminar Room',1),(12,'Activity Room',60,'Student Center','Activity Room',1),(13,'Multipurpose Hall',200,'MPH','Hall',1),(14,'Lecture Theatre 3',100,'FOM Building','Lecture Hall',1);
/*!40000 ALTER TABLE `rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `student_id` varchar(20) NOT NULL,
  `student_name` varchar(100) NOT NULL,
  `student_email` varchar(100) NOT NULL,
  `student_password` varchar(255) NOT NULL,
  `student_phone` varchar(20) DEFAULT NULL,
  `student_account_status` varchar(20) DEFAULT 'Active',
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `student_email` (`student_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES ('1221100001','Muhammad Aiman Bin Razak','muhammad.aiman.razak@student.mmu.edu.my','Aiman@001','017-6011001','Active'),('1221100002','Nur Syafiqah Binti Rahman','nur.syafiqah.rahman@student.mmu.edu.my','Syafiqah@02','017-6011002','Active'),('1221100003','Daniel Wong Wei Jian','daniel.wong.wei@student.mmu.edu.my','WeiJian#3','017-6011003','Active'),('1221100004','Aina Sofea Binti Zulkifli','aina.sofea.zulkifli@student.mmu.edu.my','Sofea@04','017-6011004','Active'),('1221100005','Arif Hakimi Bin Azlan','arif.hakimi.azlan@student.mmu.edu.my','Hakimi@05','017-6011005','Active'),('1221100006','Nur Haziqah Binti Salleh','nur.haziqah.salleh@student.mmu.edu.my','Haziqah@06','017-6011006','Active'),('1221100007','Low Jian Sheng','low.jian.sheng@student.mmu.edu.my','JSheng@07','017-6011007','Active'),('1221100008','Muhammad Irfan Bin Latif','muhammad.irfan.latif@student.mmu.edu.my','Irfan@08','017-6011008','Active'),('1221100009','Tan Mei Yi','tan.mei.yi@student.mmu.edu.my','MeiYi@09','017-6011009','Active'),('1221100010','Suresh Kumar A/L Raman','suresh.kumar.raman@student.mmu.edu.my','Suresh@10','017-6011010','Active'),('243UC245VH','Hau Lin Jun','hau.lin.jun@student.mmu.edu.my','limjun12','019-8364886','Active'),('243UC245YH','Ali Bin Azmad','ali.bin.azmad@student.mmu.edu.my','Ali_123','019-32764583','Active'),('243UC246H7','Ethan Yeo Zheng Ming','ethan.yeo.zheng@student.mmu.edu.my','yeoo456','019-7364899','Active'),('243UC246T9','Lim Mei Ling','lim.mei.ling@student.mmu.edu.my','Mei_789','019-74926499','Active'),('243UC246Y9','Fatin Najwa binti Nor Azmad','fatin.najwa@student.mmu.edu.my','fatin_995','018-4283849','Active'),('243UC247A1','Chong Wei Hong','chong.wei.hong@student.mmu.edu.my','WeiHong!1','012-1111131','Active'),('243UC247B2','Siti Nurhaliza Binti Ahmad','siti.nurhaliza.ahmad@student.mmu.edu.my','Siti@B2','012-2222242','Active'),('243UC247C3','Muthu A/L Sami','muthu.al.sami@student.mmu.edu.my','Muthu#93','012-3333363','Active'),('243UC247D4','Jessica Tan Mei Xuan','jessica.tan.mei@student.mmu.edu.my','JessMX@4','012-4444474','Active'),('243UC247E5','Ahmad Faizal Bin Hassan','ahmad.faizal.hassan@student.mmu.edu.my','Faizal@55','012-5555585','Active'),('243UC247F6','Kevin Rogers Tan Jun','kevin.rogers.tan@student.mmu.edu.my','KRtan@66','012-6666696','Active'),('243UC247G7','Nurul Izzah Binti Zainal','nurul.izzah.zainal@student.mmu.edu.my','Izzah@77','012-7777727','Active'),('243UC247H8','Lee Min Ho','lee.min.ho@student.mmu.edu.my','MinHo#88','012-8888818','Active'),('243UC247I9','Sarah Aisyah Binti Kamal','sarah.aisyah.kamal@student.mmu.edu.my','Aisyah@99','012-9999949','Active'),('243UC247J0','Wan Amirul Hakim','wan.amirul.hakim@student.mmu.edu.my','Amirul@10','013-0000030','Active');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-04 11:37:40
