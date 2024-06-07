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
- [x] Registration
- [x] Login     
- [x] profile editing
- [x] models for the admin, teacher, student
- [x] Subject model, Test models, attendence models
- [x] question making for the admin(like staff, teacher, etc)
- [x] question taking steps (like for admin all stuffs)
- [x] attendence page
- [x] attendence showing
- [x] Test making page
- [x] Test page
- [x] Result show for teacher and student
- [x] Library models
- [x] Library Pages 
- [x] Edit Profile addtion
- [x] Notifications



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

## Images
![1) home](./Images/1\)%20home.png)
### Admin
![Admin- 1) Add Admin From Excel](./Images/Admin-%201\)%20Add%20Admin%20From%20Excel.png)
![Admin- 2) Added Admins](./Images/Admin-%202\)%20Added%20Admins.png)
### Student
![Student- 4) session details](./Images/Student-%204\)%20session%20details.png)
![Student- 7) test giving](./Images/Student-%207\)%20test%20giving.png)
![Student- 9) test_result](./Images/Student-%209\)%20test_result.png)
### Teacher
![Teacher- 5) Upload question from excel for subject](./Images/Teacher-%205\)%20Upload%20question%20from%20excel%20for%20subject.png)
![Teacher- 6) Sessions](./Images/Teacher-%206\)%20Sessions.png)
![Teacher- 9) Session tests](./Images/Teacher-%209\)%20Session%20tests.png)
![Teacher- 11) test edit questions](./Images/Teacher-%2011\)%20test%20edit%20questions.png)
![Teacher- 12) Test result](./Images/Teacher-%2012\)%20Test%20result.png)