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
- [+] models for all the adminstrations
- [+] student registration 
- [ ] student login
- [ ] admin registration
- [ ] admin login
- [ ] student details filling page 
- [ ] admin details filling page
- [ ] profile making
- [ ] Subject model, Test models, etc
- [ ] question making for the admin(like staff, teacher, etc)
- [ ] question taking steps (like for admin all stuffs)
- [ ] attendence model
- [ ] attendence page
- [ ] Other things by Sir

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
