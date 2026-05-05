import mysql.connector
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import DB_CONFIG


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Student(Person):
    def __init__(self, name, stu_id, age, grade):
        super().__init__(name, age)
        self.stu_id = stu_id
        self.grade = grade
        self.attendance_percentage = {}
        self.subs = []
        self.marks = {}
    
    def get_avg_attendance(self):
        if not self.attendance_percentage: return 0.0
        return np.mean(list(self.attendance_percentage.values()))

    def print_details(self):
        print(f"Name: {self.name} | ID: {self.stu_id} | Age: {self.age}")
        print(f"Grade: {self.grade}")
        print(f"Subjects: {self.subs}")
        print(f"Marks: {self.marks}")
        print(f"Subject Attendance: {self.attendance_percentage}")
        print("-" * 40)

class School:
    def __init__(self):
        self.students = {}
    def save_data(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            for sid, s in self.students.items():
                cursor.execute("""
                    INSERT INTO students (stu_id, name, age, grade)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE                    
                    name=%s, age=%s, grade=%s      
                """, (sid, s.name, s.age, s.grade, s.name, s.age, s.grade))
                
                for sub, att in s.attendance_percentage.items():
                    cursor.execute("""
                        INSERT INTO subject_attendance (stu_id, subject, percentage)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE percentage=%s
                    """, (sid, sub, att, att))

                for sub, mark in s.marks.items():
                    cursor.execute("""
                        INSERT INTO marks (stu_id, subject, mark)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE mark=%s
                    """, (sid, sub, mark, mark))
                    
            conn.commit()
            cursor.close()
            conn.close()
            print("Data Saved to SQL Database.")
            
        except mysql.connector.Error as err:
            print(f"\n[Database Error] Could not save data: {err}")
    def load_data(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students")
            rows = cursor.fetchall()
            
            for row in rows:
                sid = row['stu_id']
                s = Student(row['name'], sid, row['age'], row['grade'])
                
                cursor.execute("SELECT subject, mark FROM marks WHERE stu_id = %s", (sid,))
                m_rows = cursor.fetchall()
                for m in m_rows:
                    s.marks[m['subject']] = m['mark']
                    if m['subject'] not in s.subs:
                        s.subs.append(m['subject'])
                        
                cursor.execute("SELECT subject, percentage FROM subject_attendance WHERE stu_id = %s", (sid,))
                for a in cursor.fetchall():
                    s.attendance_percentage[a['subject']] = a['percentage']
                    
                self.students[sid] = s
                
            cursor.close()
            conn.close()
            print("Database Loaded.")
            
        except mysql.connector.Error as err:
            print(f"\n[Database Error] Could not load data: {err}")
            print("Starting fresh.")
    def add_student(self):
        try:
            sid = int(input("Enter Student ID: "))
        except ValueError:
            print("ID must be a number.")
            return
        
        if sid in self.students:
            print("Student already exists")
            return
            
        name = input("Name: ")
        
        try:
            age = int(input("Age: "))
        except ValueError:
            print("Age must be a number. Defaulting to 0.")
            age = 0
            
        grade = input("Grade: ")
        
        self.students[sid] = Student(name, sid, age, grade)
        self.save_data()
        print("Student added")

    def update_students(self):
        try:
            sid = int(input("Enter Student ID: "))
        except ValueError: 
            print("ID must be a number.")
            return
            
        if sid in self.students:
            s = self.students[sid]
            print(f"Updating {s.name} (Press Enter to skip)")
            
            name = input(f"New Name ({s.name}): ").strip()
            if name: s.name = name
            
            age_input = input(f"New Age ({s.age}): ").strip()
            if age_input: 
                try:
                    s.age = int(age_input)
                except ValueError:
                    print("Invalid age entered. Skipping age update.")
                    
            grade = input(f"New Grade ({s.grade}): ").strip()
            if grade: s.grade = grade
            
            self.save_data()
            print("Updated.")
        else:
            print("Not found.")
    def delete_students(self):
        try:
            sid = int(input("Enter Student ID: "))
        except ValueError: return
        if sid in self.students:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE stu_id = %s", (sid,))
            conn.commit()
            cursor.close()
            conn.close()
            del self.students[sid]
            print("Student deleted")
        else:
            print("Student not found")

    

    def view_students(self):
        if not self.students:
            print("No students available")
        else:
            for s in self.students.values():
                s.print_details()
    
    def attendance(self):
        try:
            sid = int(input("Student ID: "))
        except ValueError: return
        
        if sid in self.students:
            s = self.students[sid]
            sub = input("Enter Subject for attendance: ").capitalize()
            
            current_att = s.attendance_percentage.get(sub, 0.0)
            print(f"Current Attendance for {sub}: {current_att}%")    
            try:
                new_pct = float(input(f"Enter new percentage for {sub} (0-100): "))
                if 0 <= new_pct <= 100:
                    s.attendance_percentage[sub] = new_pct
                    if sub not in s.subs: s.subs.append(sub) # Ensure subject exists in list
                    self.save_data()
                    print("Attendance Updated.")            
                    if new_pct < 75:
                        print(f"WARNING: Low attendance in {sub}!")
                else:
                    print("Must be between 0 and 100.")
            except ValueError:
                print("Invalid input.")
        else:
            print("Student not found.")

    def marks(self):
        try:
            sid = int(input("Student ID: "))
        except ValueError: return
        if sid in self.students:
            s = self.students[sid]
            while True:
                sub = input("Subject: ").capitalize()
                try:
                    mark = float(input("Marks: "))
                except ValueError: continue
                if 0 <= mark <= 100:
                    s.marks[sub] = mark
                    if sub not in s.subs:
                        s.subs.append(sub)
                    print(f"Saved {sub}: {mark}")
                else:
                    print("Marks must be 0-100.")
                if input("Add more? (y/n): ").lower() == 'n':
                    break
            self.save_data()
        else:
            print("Student not found.")

    def student_report(self):
        try:
            sid = int(input("Student ID: "))
        except ValueError: return
        if sid in self.students:
            s = self.students[sid]
            if not s.marks:
                print("No marks available")
                return
            avg = np.mean(list(s.marks.values()))
            print(f"\nReport for {s.name}")
            print(f"   Average: {avg:.2f}")
            print(f"   Attendance: {s.attendance_percentage}%")
            if 90 <= avg <= 100: print("   Grade: A")
            elif 80 <= avg < 90: print("   Grade: B")
            elif 70 <= avg < 80: print("   Grade: C")
            elif 60 <= avg < 70: print("   Grade: D")
            else: print("   Grade: F")
            print("   --- Highlights ---")
            for sub, score in s.marks.items():
                if score >= 90: print(f"   Top performer in {sub}")
                elif score < 40: print(f"   Failed in {sub}")
        else:
            print("Student not found.")

    def get_class_dataframe(self):
        data = []
        for s in self.students.values():
            avg_mark = np.mean(list(s.marks.values())) if s.marks else 0
            avg_attendance = s.get_avg_attendance()
            data.append({
                "Name": s.name, 
                "Avg Mark": round(avg_mark, 2), 
                "Avg Attendance %": round(avg_attendance, 2),
                "Status": "Pass" if avg_mark >= 40 else "Fail",
                "Attendance Alert": "LOW" if avg_attendance < 75 else "OK"
            })
        return pd.DataFrame(data)

    def class_performance_report(self):
        print("\n--- CLASS ANALYTICS (Subject-Averaged) ---")
        df = self.get_class_dataframe()
        if df.empty:
            print("No student data found.")
            return
        print(df.to_string(index=False))
        marks_array = df["Avg Mark"].to_numpy()
        att_array = df["Avg Attendance %"].to_numpy()
        print("\n" + "-"*20)
        print(f"Class Average Grade:      {np.mean(marks_array):.2f}")
        print(f"Class Average Attendance: {np.mean(att_array):.2f}%")
        print(f"Students Below 75% Att:  {len(df[df['Avg Attendance %'] < 75])}")
        print("-"*20)

    def view_top_performers(self):
        print("\nTOP PERFORMERS")
        df = self.get_class_dataframe()
        if not df.empty:
            top_df = df.sort_values(by="Avg Mark", ascending=False).head(3)
            print(top_df[["Name", "Avg Mark", "Status"]].to_string(index=False))
        else:
            print("No data.")

    def view_low_attendance_list(self):
        print("\nLOW ATTENDANCE LIST (<75%)")
        df = self.get_class_dataframe()
        if not df.empty:
            low_att = df[df["Avg Attendance %"] < 75]
            if not low_att.empty:
                print(low_att[["Name", "Avg Attendance %"]].to_string(index=False))

    def generate_graphs(self):
        df = self.get_class_dataframe()
        if df.empty:
            print("No data to plot.")
            return
        print("\n--- GENERATING GRAPHS ---")
        print("1. Student Performance (Average Marks)")
        print("2. Class Attendance Overview (Threshold 75%)")
        print("3. Subject-wise Attendance (Specific Student)")
        print("4. Subject-wise Class Performance")
        try:
            choice = int(input("Choose graph type (1-3): "))
        except ValueError: return
        df = self.get_class_dataframe()
        if df.empty:
            print("No data to plot.")
            return
        if choice == 1:
            plt.figure(figsize=(10, 6))
            plt.scatter(df["Avg Attendance %"], df["Avg Mark"], color='purple')
            for i, txt in enumerate(df["Name"]):
                plt.annotate(txt, (df["Avg Attendance %"][i], df["Avg Mark"][i]))
            plt.title("Attendance vs. Performance Correlation")
            plt.xlabel("Average Attendance %")
            plt.ylabel("Average Marks")
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.show()
        elif choice == 2:
            plt.figure(figsize=(10, 6))
            colors = ['red' if x < 75 else 'green' for x in df["Avg Attendance %"]]
            plt.bar(df["Name"], df["Avg Attendance %"], color=colors)
            plt.axhline(y=75, color='darkred', linestyle='--', label='75% Requirement')
            plt.title("Total Class Attendance (Averaged Across Subjects)")
            plt.ylabel("Attendance %")
            plt.legend()
            plt.show() 
        
        elif choice == 3: 
            sid = int(input("Enter Student ID: "))
            if sid in self.students:
                s = self.students[sid]
                if s.attendance_percentage: 
                    subs = list(s.attendance_percentage.keys())
                    atts = list(s.attendance_percentage.values())
                    plt.bar(subs, atts, color='orange')
                    plt.title(f"Subject-wise Attendance for {s.name}")
                    plt.ylim(0, 105)
                    plt.show()
        elif choice == 4:
            subject_totals, subject_counts = {}, {}
            for s in self.students.values():
                for sub, mark in s.marks.items():
                    subject_totals[sub] = subject_totals.get(sub, 0) + mark
                    subject_counts[sub] = subject_counts.get(sub, 0) + 1
            if subject_totals:
                subjects = list(subject_totals.keys())
                avgs = [subject_totals[s]/subject_counts[s] for s in subjects]
                plt.bar(subjects, avgs, color='orange')
                plt.title("Class Average per Subject")
                plt.ylabel("Marks")
                plt.ylim(0, 100)
                plt.savefig("subject_graph.png")
                plt.show()
            else:
                print("No subject data.")

    def import_from_excel(self):
        file_path = input("Enter the path to the Excel file (e.g., students.xlsx): ").strip()
        try:
            df = pd.read_excel(file_path)
            
            for _, row in df.iterrows():
                sid = int(row['stu_id'])
                
                if sid not in self.students:
                    name = str(row['name'])
                    age = row['age']
                    grade = row['grade']
                    
                    new_student = Student(name, sid, age, grade)
                    self.students[sid] = new_student
                    print(f"Imported: {name} (ID: {sid})")
                else:
                    print(f"Skipped: ID {sid} already exists.")
            
            self.save_data()
            print("\nBulk Import Successful and Saved to Database.")
            
        except FileNotFoundError:
            print("Error: File not found. Please check the path.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":  # to check if the code is run from the main file and not imported if imported then the parent name will be there or else main aayega
    obj = School()
    obj.load_data()
    while True:
        print("\n" + "="*30)
        print("1. Add Student | 2. Update | 3. Delete | 4. View All")
        print("5. Attendance | 6. Add Marks | 7. Report | 8. Analytics")
        print("9. Graphs | 10. Top Performers | 11. Low Attendance | 12. Add Multiple Students | 13. Exit")
        try:
            ch = int(input("Choice: "))
            if ch == 1: obj.add_student()
            elif ch == 2: obj.update_students()
            elif ch == 3: obj.delete_students()
            elif ch == 4: obj.view_students()
            elif ch == 5: obj.attendance()
            elif ch == 6: obj.marks()
            elif ch == 7: obj.student_report()
            elif ch == 8: obj.class_performance_report()
            elif ch == 9: obj.generate_graphs()
            elif ch == 10: obj.view_top_performers()
            elif ch == 11: obj.view_low_attendance_list()
            elif ch == 12: obj.import_from_excel()
            elif ch == 13: 
                print("Goodbye")
                break
        except ValueError: 
            continue