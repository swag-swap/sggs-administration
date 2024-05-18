# SGGS Administration Website
This website is the administration website for the SGGS college management. There are some main sections in the website like :
- Registration on website.
- Data of the user.
- Login as student or administration faculty.

#### 1) As a student login
- Fill up the requied details like documents, fees, hostel or not, hostel docs, Year of study, etc
- Attendence for students for specific subject

#### 2) As a admin login
- Fill up required details, for job kind of thing. What kind of admin like Teacher, Staff, for what role, 
- If admin is like the staff, then they can make their own questions for specific subjects
- If admin is like teacher, then they can create the questions for the test and make the random choices for it also.
- Teacher can also add the staff member for his specific subject.
- Staff has its specific role of doing things.

## Todo
- [+] Registration
- [+] Login 
- [+] profile editing
- [+] models for the admin, teacher, student
- [+] Subject model, Test models, attendence models
- [+] question making for the admin(like staff, teacher, etc)
- [+] question taking steps (like for admin all stuffs)
- [+] attendence page
- [+] attendence showing
- [+] Test making page
- [+] Test page
- [ ] Result show for teacher and student
- [+] Library models
- [+] Library Pages 



## Steps to create the project
1) Creating the virtual environment.
    ```
    sudo apt-get install -y python3-venv
    python3 -m venv venv
    ````
2) Creating the project in Django.
    ```
    django-admin startproject sggs
    ```
3) Adding requirements in requirements.txt
    ```
    pip freeze > requirements.txt
    ```
4) Collecting the static files
    ```
    python3 manage.py collectstatic
    ```
5) Change the source 
    ```
    source venv/bin/activate
    ```

6) For installing the requirement.txt
    pip install -r requirements.txt

## Notification numbers
1) Teacher Profile Update Notification:  
2) New Teacher Request Notification:  
3) New Student Enrollment Notification:  
4) Fee Payment Reminder Notification:  
5) Class Session Notification:  
6) Exam Schedule Notification:  
7) Attendance Notification:  
8) Assignment Submission Notification:  
9) Grading Notification: 
10) System Maintenance Notification: