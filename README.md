# Smart-Placement-Analytics
Smart Placement Analytics &amp; Recommendation System using Python and MySQL. The system cleans placement data, performs analytics and visualization, and recommends suitable companies and job roles based on department, CGPA, and skills.

# Smart Placement Analytics & Recommendation System

A Python and MySQL-based desktop application for cleaning placement data, performing placement analytics, visualizing results, and recommending suitable companies and job roles based on a student's department, CGPA, and skills.

## 📌 Project Overview

The **Smart Placement Analytics & Recommendation System** is designed to help students and placement coordinators manage and analyze placement-related data efficiently.

The system allows placement data to be imported from Excel or CSV files, cleaned and validated using Python and Pandas, stored in a MySQL database, and analyzed through graphical reports.

The system also provides a **rule-based placement recommendation module** that compares a student's department, CGPA, and skills with predefined company eligibility criteria and recommends suitable companies and job roles.

## 🎯 Objectives

- Import placement data from Excel and CSV files.
- Clean and validate placement datasets.
- Remove duplicate and invalid records.
- Store processed placement data in MySQL.
- Perform placement-related statistical analysis.
- Generate graphical visualizations.
- Recommend suitable companies and job roles.
- Export processed data and results.
- Provide a simple and user-friendly desktop interface.

## ✨ Features

### 1. Data Import
- Import placement data from Excel and CSV files.
- Read datasets using Pandas.
- Validate imported data.

### 2. Data Cleaning
- Remove duplicate records.
- Handle missing values.
- Clean inconsistent text values.
- Validate important placement fields.
- Prepare data for database storage and analysis.

### 3. Database Management
- Store cleaned student placement data in MySQL.
- Store company and job eligibility information.
- Retrieve placement and company offer records.
- Use MySQL Connector/Python for database connectivity.

### 4. Placement Analytics
The system can perform analysis such as:

- Total number of students.
- Number of placed students.
- Placement percentage.
- Average package.
- Highest package.
- Department-wise placement statistics.

### 5. Data Visualization
The system uses Matplotlib to generate graphical representations of placement data.

Examples include:

- Department-wise placement analysis.
- Placement status analysis.
- Package-related analysis.
- Other placement statistics.

### 6. Smart Placement Recommendation

The recommendation module uses a **rule-based eligibility and skill-matching algorithm**.

The system:

1. Checks whether the student's department matches the company requirement.
2. Checks whether the student's CGPA satisfies the minimum CGPA requirement.
3. Compares the student's skills with the required company skills.
4. Calculates the percentage of required skills matched.
5. Recommends suitable companies and job roles.
6. Uses package information to sort eligible recommendations.

The system does **not** recommend companies only on the basis of the highest package.

### 7. Export
- Export processed placement data.
- Save analysis-related results for further use.

## 🧠 Recommendation Algorithm

The project uses a **Rule-Based Recommendation Algorithm**.

### Input

The student provides:

- Department
- CGPA
- Skills

### Company Data

The system uses:

- Company name
- Job role
- Department
- Minimum CGPA
- Required skills
- Package

### Matching Process

```text
Student Profile
      ↓
Check Department
      ↓
Check CGPA Eligibility
      ↓
Compare Student Skills
      ↓
Calculate Skill Match
      ↓
Find Eligible Companies
      ↓
Display Recommended Job Roles
