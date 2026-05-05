# 🎓 Student Management System (Python + MySQL)

A command-line Student Management System built with **Python** and **MySQL**. It supports full CRUD operations, attendance and marks tracking, performance analytics, data visualisation, and bulk import from Excel — all backed by a persistent MySQL database.

---

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Visualisations](#visualisations)
- [Excel Import](#excel-import)

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | Add Student | Register a new student with ID, name, age, and grade |
| 2 | Update Student | Edit existing student details |
| 3 | Delete Student | Remove a student and all linked records |
| 4 | View All | Display full details of every student |
| 5 | Attendance | Set/update subject-wise attendance percentage with low-attendance alerts |
| 6 | Add Marks | Enter marks per subject (supports multiple subjects in one session) |
| 7 | Student Report | Per-student report: average marks, letter grade (A–F), highlights |
| 8 | Class Analytics | Class-wide averages for marks and attendance via Pandas DataFrame |
| 9 | Graphs | 4 matplotlib chart types (see [Visualisations](#visualisations)) |
| 10 | Top Performers | Shows top 3 students by average mark |
| 11 | Low Attendance | Lists all students below 75% average attendance |
| 12 | Bulk Import | Import multiple students at once from an `.xlsx` file |

---

## 🗂️ Project Structure

```
Student-Management-SQL--main/
├── major_final_sql.py    # Main application (Person, Student, School classes)
├── config.py             # MySQL connection configuration
├── major_excel_data.xlsx # Sample Excel file for bulk student import
└── README.md
```

### Class Design

```
Person
  └── Student          # name, age, stu_id, grade, marks{}, attendance_percentage{}, subs[]
School                 # Manages a dict of Students; handles all DB + UI operations
```

---

## 🗄️ Database Schema

The application uses a MySQL database named `school_db` with three tables:

```sql
-- Student core info
CREATE TABLE students (
    stu_id INT PRIMARY KEY,
    name   VARCHAR(100),
    age    INT,
    grade  VARCHAR(10)
);

-- Subject-wise attendance
CREATE TABLE subject_attendance (
    stu_id     INT,
    subject    VARCHAR(50),
    percentage FLOAT,
    PRIMARY KEY (stu_id, subject),
    FOREIGN KEY (stu_id) REFERENCES students(stu_id)
);

-- Subject-wise marks
CREATE TABLE marks (
    stu_id  INT,
    subject VARCHAR(50),
    mark    FLOAT,
    PRIMARY KEY (stu_id, subject),
    FOREIGN KEY (stu_id) REFERENCES students(stu_id)
);
```

> All writes use `INSERT ... ON DUPLICATE KEY UPDATE` for safe upserts.

---

## ✅ Prerequisites

- Python 3.8+
- MySQL Server 8.0+
- The following Python packages:

```
mysql-connector-python
numpy
pandas
matplotlib
openpyxl
```

---

## 🚀 Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/maanyafadia1903-dotcom/Student-Management-SQL-.git
   cd Student-Management-SQL--main
   ```

2. **Install dependencies**
   ```bash
   pip install mysql-connector-python numpy pandas matplotlib openpyxl
   ```

3. **Create the MySQL database and tables**
   ```sql
   CREATE DATABASE school_db;
   USE school_db;

   CREATE TABLE students (
       stu_id INT PRIMARY KEY,
       name   VARCHAR(100),
       age    INT,
       grade  VARCHAR(10)
   );

   CREATE TABLE subject_attendance (
       stu_id     INT,
       subject    VARCHAR(50),
       percentage FLOAT,
       PRIMARY KEY (stu_id, subject),
       FOREIGN KEY (stu_id) REFERENCES students(stu_id)
   );

   CREATE TABLE marks (
       stu_id  INT,
       subject VARCHAR(50),
       mark    FLOAT,
       PRIMARY KEY (stu_id, subject),
       FOREIGN KEY (stu_id) REFERENCES students(stu_id)
   );
   ```

4. **Configure your credentials** (see [Configuration](#configuration))

5. **Run the application**
   ```bash
   python major_final_sql.py
   ```

---

## 💻 Usage

On launch the app loads all existing data from MySQL, then shows an interactive menu:

```
==============================
1. Add Student | 2. Update | 3. Delete | 4. View All
5. Attendance | 6. Add Marks | 7. Report | 8. Analytics
9. Graphs | 10. Top Performers | 11. Low Attendance | 12. Add Multiple Students | 13. Exit
```

All changes are automatically persisted to MySQL after each operation.

### Grading Scale

| Average Marks | Grade |
|:---:|:---:|
| 90 – 100 | A |
| 80 – 89  | B |
| 70 – 79  | C |
| 60 – 69  | D |
| Below 60 | F |

> Students with attendance below **75%** in any subject receive an automatic warning.

---

## 📊 Visualisations

Option **9 → Graphs** offers four chart types:

| Choice | Chart | Description |
|--------|-------|-------------|
| 1 | Scatter plot | Attendance % vs. Average Marks correlation |
| 2 | Bar chart | Class attendance — green (≥75%), red (<75%), with 75% threshold line |
| 3 | Bar chart | Subject-wise attendance for a specific student |
| 4 | Bar chart | Class average marks per subject (also saves `subject_graph.png`) |

---

## 📥 Excel Import

Use option **12** to bulk-import students from an Excel file.

The `.xlsx` file must contain these columns:

| stu_id | name | age | grade |
|--------|------|-----|-------|
| 101 | Maanya Fadia | 20 | 11 |
| 102 | Riya Shah | 21 | 12 |

A sample file (`major_excel_data.xlsx`) is included in the repository.

---

## 👩‍💻 Author

**Maanya Fadia**  
GitHub: [@maanyafadia1903-dotcom](https://github.com/maanyafadia1903-dotcom)
