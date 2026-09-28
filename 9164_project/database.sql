CREATE DATABASE IF NOT EXISTS placement_db;
USE placement_db;
CREATE TABLE IF NOT EXISTS students (
 student_id VARCHAR(20) PRIMARY KEY, student_name VARCHAR(100), department VARCHAR(100),
 cgpa DECIMAL(4,2), skills VARCHAR(500), placement_status VARCHAR(30),
 company VARCHAR(100), package_lpa DECIMAL(6,2));
CREATE TABLE IF NOT EXISTS company_offers (
 offer_id INT PRIMARY KEY, company VARCHAR(100), job_role VARCHAR(100),
 department VARCHAR(100), min_cgpa DECIMAL(4,2), required_skills VARCHAR(500),
 package_lpa DECIMAL(6,2));