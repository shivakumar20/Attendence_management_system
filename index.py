# ALL THE IMPORTS
import datetime as dt
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_session import Session
from barreader import BarcodeReader
import os, csv, testing3_face, redis, psycopg2
from datetime import timedelta

from sqlalchemy import inspect, null

app = Flask(__name__)

# FOR CORS
CORS(app)

# INITIALIZING THE BCRYPT
bcrypt = Bcrypt(app)

app.secret_key = "khajashaik"
app.config['SESSION_TYPE'] = 'redis'

# FOR SAVING FILES INTO THE SERVER
UPLOAD_FOLDER = 'uploaded_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# PASSWORD AND URI DETAILS OF PGADMIN DATABASE
password = "khajashaik"
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{password}@localhost/review2database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# REDIS SESSION DETAILS AND ALSO BE IMPLEMENTED FOR CACHE
SESSION_PERMANENT=False
SESSION_USE_SIGNER=True
SESSION_REDIS=redis.from_url("redis://127.0.0.1:6379")


# INITIALIZING THE SERVER SESSION
server_session=Session(app)

# FOR GETTING THE UNIQUE ID'S FOR ALL
def get_uuid():
    return uuid4().hex

# FOR THE CONNECTION OF DATABASE
conn = psycopg2.connect(
        host="localhost",
        database="intelliproctor",
        user="postgres",
        password="1234"
    )

# ---> DATABASE MODELS STARTS HERE

# ADMIN'S LOGIN TABLE
class Admin(db.Model):
    id = db.Column(db.Text, nullable=False, primary_key=True, default=get_uuid)
    adminid = db.Column(db.String(10), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.Text, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# TEACHER'S LOGIN TABLE 
class Teacher(db.Model):
    id = db.Column(db.Text, nullable=False, primary_key=True, default=get_uuid)
    teacherid = db.Column(db.String(10), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.Text, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# STUDENT'S LOGIN TABLE
class Student(db.Model):
    id = db.Column(db.Text, nullable=False, primary_key=True, default=get_uuid)
    stuid = db.Column(db.String(20), nullable=False, unique=True)
    section = db.Column(db.Integer, nullable=False)
    password = db.Column(db.Text, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# TEACHER'S DETAILS TABLE
class Teacherdetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(15), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    course = db.Column(db.String(30), nullable=False)
    section = db.Column(db.Integer, nullable=False)
    courseid = db.Column(db.String(30), nullable=False)
    seccourseid = db.Column(db.String(30), nullable=False)

@app.route('/forsession')
def forsession():
    return session['stuid'].get('one')

#TODO : CLICKING ON PARTICULAR SUBJECT, IT NEEDS TO FETCH THE ATTENDANCE OF IT THROUGH OUT THE SEMESTER FOR A STUDENT

# FOR FETCHING STUDENT LOGIN PAGE AND THE ATTENDANCE
@app.route('/')
def student_login_page():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)
    try:
        if session['stuid'] is not null:
            result = Student.query.filter_by(stuid=session['stuid'].get('one')).first()

            cur = conn.cursor()
            query = "SELECT * FROM {} WHERE uid = '{}'".format('section'+str(result.section), session['stuid'].get('one'))
            cur.execute(query)
            r = cur.fetchall()
            print(r)

            query = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{}'".format('section'+str(result.section))
            cur.execute(query)
            result = cur.fetchall()
            print(result)

            forSubjects = []
            forAtt = []
            for i in range(3, len(r[0])):
                forAtt.append(r[0][i])
            for i in range(3, len(result)):
                for j in result[i]:
                    forSubjects.append(j)

            print(forAtt)
            print(forSubjects)

            attendance = {}
            for i, j in zip(forAtt, forSubjects):
                attendance[j] = i

            return render_template('/stu_profile.html', attendance = attendance)
    except:
        return render_template('/stu_login.html')

# FOR AUTHENTICATING THE STUDENT LOGIN 
@app.route('/login_student', methods=['POST'])
def login_student():
    stuid = request.form['id']
    studentPassword = request.form['password']

    if(stuid and studentPassword):
        student = Student.query.filter_by(stuid=stuid).first()

        if student:
            if student.stuid != stuid:
                flash("Invalid credentials")
                return render_template('/stu_login.html')

            if not bcrypt.check_password_hash(student.password, studentPassword):
                flash("Invalid credentials")
                return render_template('/stu_login.html')
        
            session['stuid'] = {'one': stuid}

            return redirect('/')

        flash("No data about you in the database")
        return render_template('/stu_login.html')

    flash("All fields are required")
    return render_template('/stu_login.html')

# FOR TEACHER LOGIN PAGE
@app.route('/teacher', methods=['GET', 'POST'])
def teacher_login_page():
    session.permanent = True
    # app.permanent_session_lifetime = timedelta(minutes=1)
    try:
        if session['teaid'] is not null:
            allSections = Teacherdetails.query.filter_by(uid=session['teaid'].get('one')).all()
            for values in allSections:
                print(values.uid, values.name, values.course, values.section, values.courseid, values.seccourseid)
            return render_template('/tea_profile.html', allSections=allSections)
    except:
        return render_template('/tea_login.html')

# FOR AUTHENTICATING THE TEACHER LOGIN 
@app.route('/login_teacher', methods=['POST'])
def login_teacher():
    teaid = request.form['id']
    name = request.form['name']
    teaPassword = request.form['password']

    if(teaid and name and teaPassword):
        teacher = Teacher.query.filter_by(teacherid=teaid).first()

        if teacher:
            if teacher.teacherid != teaid:
                flash("Invalid credentials")
                return render_template('/tea_login.html')

            if teacher.username != name:
                flash("Invalid credentials")
                return render_template('/tea_login.html')

            if not bcrypt.check_password_hash(teacher.password, teaPassword):
                flash("Invalid credentials")
                return render_template('/tea_login.html')
        
            session['teaid'] = {'one': teaid, 'two':name}

            return redirect('/teacher')

        flash("No data about you in the database")
        return render_template('/tea_login.html')

    flash("All fields are required")
    return render_template('/tea_login.html')

@app.route('/sec_att', methods=['POST'])
def sec_att():
    try:
        teaid = session['teaid'].get('one')
    except:
        return render_template('/tea_login.html')

    print(request)
    course = ''
    section = request.form['forSection']
    teaid = session['teaid'].get('one')

    try:
        course = request.form['course']
    except:
        courseid = request.form['courseid']
        asdf = Teacherdetails.query.filter_by(uid=teaid, courseid=courseid.upper(), section=section).first()
        course = asdf.course


    result = Teacherdetails.query.filter_by(uid=teaid, course=course.upper(), section=section).first()
    r = result

    cur = conn.cursor()
    query = 'SELECT * FROM {}'.format(result.courseid.lower()+section)
    cur.execute(query)
    result = cur.fetchall()
    
    cur = conn.cursor()
    query = 'SELECT uid, name, section, {} FROM {}'.format(course.lower(), 'section'+section)
    cur.execute(query)
    result1 = cur.fetchall()
    print(result1)

    return render_template('tea_sec_att.html', result=result, course=course, result1=result1, courseid=r.courseid.upper(), section=section)

@app.route('/show_att', methods=['POST'])
def show_att():
    try:
        teaid = session['teaid'].get('one')
    except:
        return render_template('/tea_login.html')
    print('hai need to fetch the date dude')
    date = request.form['date']
    courseid = request.form['courseid']
    section = request.form['section']

    isData = True
    result = ''

    cur = conn.cursor()
    cur = conn.cursor()
    query = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{}'".format(courseid.lower()+section)
    cur.execute(query)
    allcolumns = cur.fetchall()

    print(allcolumns)
    print(courseid.upper()+section+" "+date)

    flag = False
    for i in allcolumns:
        for j in i:
            if j == courseid.upper()+section+" "+date:
                flag = True
                break

    print(flag)
    if flag:
        cur = conn.cursor()
        query = 'SELECT id, name, \"{}\" from {}'.format(courseid.upper()+section+" "+date, courseid.lower()+section)
        cur.execute(query)
        result = cur.fetchall()
    else:
        isData = False

    return render_template('show_att.html', isData = isData, result = result, courseid=courseid, section=section, date=date)

# FOR REGISTERING THE ADMIN
@app.route('/register')
def register():
    return render_template('register_admin.html')

# FOR ADMIN LOGIN PAGE
@app.route('/admin')
def admin_login_page():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1) 
    try:
        if session['adminid'] is not null:
            return render_template('adm_profile.html')
    except:
        return render_template('adm_login.html')

# REGISTERING THE NEW ADMIN
@app.route('/register_admin', methods=['POST'])
def register_admin():
    adminid = request.form['id']
    name = request.form['name']
    password = request.form['password']

    if(adminid and name and password):

        admin_exists = Admin.query.filter_by(adminid = adminid).first() is not None

        if admin_exists:
            flash("Admin already exists")  
            return render_template('register_admin.html')
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        newAdmin = Admin(adminid=adminid, username=name, password=hashed_password)

        db.session.add(newAdmin)
        db.session.commit()
        session['adminid'] = {'one':adminid, 'two':name}

        return redirect('/admin')

    flash("All fields are required")  
    return render_template('register_admin.html')

# FOR AUTHENTICATING THE ADMIN LOGIN 
@app.route('/login_admin', methods=['POST'])
def login_admin():
    adminid = request.form['id']
    name = request.form['name']
    adminPassword = request.form['password']

    if(adminid and name and adminPassword):
        admin = Admin.query.filter_by(adminid=adminid).first()

        if admin:
            if admin.adminid != adminid:
                flash("Invalid credentails")
                return render_template('adm_login.html')
            
            if admin.username != name:
                flash("Invalid credentails")
                return render_template('adm_login.html')

            if not bcrypt.check_password_hash(admin.password, adminPassword):
                flash("Invalid credentails")
                return render_template('adm_login.html')
        
            session['adminid'] = {'one': adminid, 'two':name}

            return redirect('/admin')

        flash("No data about you in the database")
        return render_template('adm_login.html')

    flash("All fields are required")
    return render_template('adm_login.html')

# FOR SHOWING THE ADMIN PROFILE
@app.route('/admin_profile')
def admin_profile():
    try:
        admminid = session['adminid'].get('one')
        return render_template('adm_profile.html')
    except:
        return render_template('adm_login.html')

# ADDING THE TEACHERS DETAILS BY ADMIN
@app.route('/add', methods=['POST']) 
def add():
    try:
        admminid = session['adminid'].get('one')
    except:
        return render_template('adm_login.html')

    uid = request.form['uid']
    name = request.form['name']
    course = request.form['course']
    section = request.form['section']
    courseid = request.form['courseid']

    # ASSUMING THAT SECTION TABLE IS ALREADY PRESENT
    if uid and name and course and section and courseid: 

        inspecter = inspect(db.engine)

        if inspecter.has_table('section'+section) is False:
            flash("Section was not created yet")
            return render_template('adm_profile.html')

        # NEW TEACHER WILL BE CREATED WITH CREDENTIALS AND DETAILS WILL ALSO BE ADDED. 

        checkTeacher = Teacher.query.filter_by(teacherid=uid).first()

        if checkTeacher is None:
            newTeacher = Teacher(teacherid=uid, username=name, password=bcrypt.generate_password_hash(name).decode('utf-8'))
            db.session.add(newTeacher)

        details = Teacherdetails(uid=uid, name=name, course=course, section=section, courseid=courseid, seccourseid=section+ " " + courseid)

        db.session.add(details)
        db.session.commit()
        cur = conn.cursor()

        # CREATE A ATTENDANCE TABLE FOR THAT TEACHER, FOR THAT SECTION, FOR THAT SUBJECT
        if inspecter.has_table(courseid.lower()+section):
            flash("Some error has occured while adding teacher.")
            return render_template('adm_profile.html')

        table = 'CREATE TABLE {} (id VARCHAR(20) NOT NULL, name VARCHAR(20) NOT NULL)'.format(courseid+section)
        cur.execute(table)
        conn.commit()

        students = 'SELECT uid, name from {}'.format('section'+section)
        cur.execute(students)
        result = cur.fetchall()
        print(result)

        # ADD THESE STUDENTS DATA INTO ANOTHER TABLE FOR FUTURE ATTENDANCE
        for values in result:
            query = 'INSERT INTO {} (id, name) VALUES {}'.format(courseid+section, values)
            cur.execute(query)
            print(query)

        # FOR ADDING THE COURSE TABLE TO THE STUDENTS TABLE
        addColumn = 'ALTER TABLE {} ADD COLUMN {} VARCHAR(15) CONSTRAINT zero_attendance DEFAULT 0'.format('section'+section, course)
        cur.execute(addColumn)
        conn.commit()
        
        flash("Teacher details were added successfully")
        return render_template('adm_profile.html')
    flash("All details of teachers are required")
    return render_template('adm_profile.html')

# FOR UPLOADING THE FILE OF STUDENTS
@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        admminid = session['adminid'].get('one')
    except:
        return render_template('adm_login.html')

    file = request.files['csv']
    section = request.form['section']

    imagesfile = request.files.getlist('imagesfile')

    inspecter = inspect(db.engine)

    if file and section:
        if inspecter.has_table('section'+section):
            flash("Section was already added")  
            return redirect(url_for('admin_profile'))
        else:     
            cur = conn.cursor()
            table = 'create table {} (uid VARCHAR(20) NOT NULL, name VARCHAR(20) NOT NULL, section INTEGER NOT NULL)'.format('section'+section)   

            cur.execute(table)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            file = open(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            
            csvreader = csv.reader(file)
            i=0
            for row, file in zip(csvreader, imagesfile):
                record = 'INSERT INTO {} (uid, name, section) VALUES (%s, %s, %s)'.format('section'+section)
                if i==0:
                    row[0] = row[0][3:]
                file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/images', row[0]+'.png'))
                values = (row[0], row[1], row[2])
                cur.execute(record, values)
                print(i, row[0], type(row[0]))
                query = Student(stuid=row[0], section=row[2], password=bcrypt.generate_password_hash(row[0]).decode('utf-8'))
                db.session.add(query)
                i=i+1

            db.session.commit()
            conn.commit()
            file.close()
            cur.close()

            flash("File was uploaded successfully")  
            return redirect(url_for('admin_profile'))
    flash("All details are required to add a section")  
    return redirect(url_for('admin_profile'))

# FOR STUDENT ATTENDANCE PORTAL
@app.route('/check_att', methods=['POST', 'GET'])
def check_att():
    return render_template('attendance.html', first=True) 

# FOR CLEARING THE SESSIONS OF A PARTICULAR SESSION
@app.route('/flaskBro', methods=['POST'])
def flaskBro():
    fromis = request.form['from']
    togo = request.form['togo']
    try:
        session.pop(fromis)
        return redirect(togo)
    except:
        return redirect(togo)

# FOR CHECKING THE ATTENDANCE
@app.route('/attendance', methods=['POST'])
def attendance():
    course = request.form['course']
    section = request.form['section']

    result = Teacherdetails.query.filter_by(course=course.upper(), section=section).first()

    if result:
        now = dt.date.today()
        cur = conn.cursor()
        query = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{}'".format(result.courseid.lower()+section)
        cur.execute(query)
        results = cur.fetchall()

        for values in results:
            for val in values:
                if result.courseid+section+" "+str(now) == val:
                    return render_template('attendance.html', first=False, tableis=(result.courseid+section+" "+str(now)), course=course, section=section)
        flash("Attendance was not started yet")
        return render_template('/attendance.html', first=True)

    flash("Some error for taking attendance for this subject")
    return render_template('/attendance.html', first=True)

@app.route('/start_att', methods=['POST', 'GET'])
def start_att():
    try:
        teaid = session['teaid'].get('one')
    except:
        return render_template('/tea_login.html')

    course = request.form['course']
    section = request.form['section']
    teaid = session['teaid'].get('one')

    data = Teacherdetails.query.filter_by(uid = teaid, course=course).first()

    cur = conn.cursor()

    now = dt.date.today()

    # NEED TO SOLVE THE TWO DAYS ATTENDANCE FOR A SAME SUBJECT IF U WANT

    cur = conn.cursor()
    query = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{}'".format(data.courseid.lower()+section)
    cur.execute(query)
    results = cur.fetchall()
    print(results)

    for values in results:
        for val in values:
            if val == data.courseid.upper()+section + " " + str(now):
                flash("Attendance was already started for today")
                allSections = Teacherdetails.query.filter_by(uid=session['teaid'].get('one')).all()
                return render_template('/tea_profile.html', allSections=allSections)

    inspecter = inspect(db.engine)


    query = 'ALTER TABLE {} ADD COLUMN "{}" INTEGER CONSTRAINT zero_attendance DEFAULT 0'.format(data.courseid+section, data.courseid+section+" "+str(now))

    cur.execute(query)
    conn.commit()

    allSections = Teacherdetails.query.filter_by(uid=session['teaid'].get('one')).all()
    flash("Attendance has started")
    return render_template('/tea_profile.html', allSections=allSections)

# FOR STORING IMAGES
@app.route('/capture_img', methods=['POST'])
def capture_img():
    stuid = BarcodeReader(request.form["img1"])
    print(len(stuid))
    if len(stuid) != 0:
        msg = testing3_face.save_img(request.form["img"], stuid)
        if len(msg) == 16:
            tableis = request.form['tableis']
            course = request.form['course']
            section = request.form['section']

            if msg == 'no':
                return msg;
            cur = conn.cursor()
            adsaf = msg.split('.')[0]
            print(adsaf)

            query = "SELECT \"{}\" FROM {} WHERE id = '{}'".format(tableis, tableis.split(' ')[0].lower(), stuid)
            cur.execute(query)
            result = cur.fetchall()

            for res in result:
                for r in res:
                    r = r+1
                    query = "UPDATE {} SET \"{}\" = {} WHERE id = '{}'".format(tableis.split(' ')[0].lower(), tableis, r, stuid)
                    cur.execute(query)
                    conn.commit()

            query = "SELECT \"{}\" FROM {} WHERE uid = '{}'".format(course.lower(), 'section'+section, stuid)
            print(query)
            cur.execute(query)
            result = cur.fetchall()
            print(result)

            for res in result:
                for r in res:
                    r = int(r) + 1
                    query = "UPDATE {} SET \"{}\" = {} WHERE uid='{}'".format('section'+section, course.lower(), r, stuid)
                    cur.execute(query)
                    conn.commit()

        return msg
    else:
        return 'bar'


if __name__ == '__main__':
    app.run(debug=True)