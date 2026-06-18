import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, abort
from database import db, init_db
from models import Student, Grade, ReportCard
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ---------- DATABASE SETUP (centralized) ----------
init_db(app)

# ---------- AUTO-SEED ADMIN ----------
with app.app_context():
    if not Student.query.filter_by(username='admin').first():
        admin = Student(
            student_id_code='000000',
            name='Master Admin',
            father_name='System',
            role='admin',
            username='admin',
            email='admin@system.com',
            contact='00000000000',
            qualifications='Root',
            password='admin123'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin injected.")

# ---------- AUTH CHECK ----------
@app.before_request
def require_login():
    if request.endpoint in ('login', 'logout') or request.path.startswith('/static'):
        return
    if 'user_id' not in session:
        return redirect(url_for('login'))

# ----------------- LOGIN -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Student.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            return redirect(url_for('index'))
        error = "Invalid Username or Password!"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----------------- DASHBOARD -----------------
@app.route('/')
def index():
    total_students = Student.query.filter_by(role='student').count()
    total_teachers = Student.query.filter_by(role='teacher').count()
    recent_activities = ReportCard.query.order_by(ReportCard.id.desc()).limit(5).all()
    return render_template('index.html',
                           student_count=total_students,
                           teacher_count=total_teachers,
                           recent_activities=recent_activities)

# ----------------- STUDENT DIRECTORY -----------------
@app.route('/students')
def manage_students():
    all_users = Student.query.all()
    return render_template('students.html', users=all_users)

# ----------------- ADD NEW USER -----------------
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        username = request.form.get('username')
        father_name = request.form.get('father_name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        qualifications = request.form.get('qualifications')

        while True:
            code = str(random.randint(100000, 999999))
            if not Student.query.filter_by(student_id_code=code).first():
                break

        new_user = Student(
            student_id_code=code,
            name=name,
            father_name=father_name,
            role=role,
            username=username,
            email=email,
            contact=contact,
            qualifications=qualifications,
            password='admin123'
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('manage_students'))
    return render_template('student_form.html')

# ----------------- GRADING DASHBOARD -----------------
@app.route('/grading_dashboard')
def grading_dashboard():
    all_students = Student.query.filter_by(role='student').all()
    return render_template('grading_form.html', students=all_students)

# ----------------- PREVIEW REPORT -----------------
@app.route('/preview_report', methods=['POST'])
def preview_report():
    student_id = request.form.get('student_id')
    student = Student.query.get(student_id)
    if not student:
        return "Student not found.", 404

    total_days = int(request.form.get('total_days') or 1)
    attended_days = int(request.form.get('attended_days') or 0)

    if total_days <= 0:
        total_days = 1
    if attended_days > total_days:
        attended_days = total_days

    attendance_perc = round((attended_days / total_days) * 100, 2)

    eng = int(request.form.get('eng') or 0)
    urdu = int(request.form.get('urdu') or 0)
    math = int(request.form.get('math') or 0)
    phy = int(request.form.get('phy') or 0)
    cs = int(request.form.get('cs') or 0)
    prog = int(request.form.get('prog') or 0)
    db_sys = int(request.form.get('db_sys') or 0)

    obtained = eng + urdu + math + phy + cs + prog + db_sys
    total = 700
    percentage = round((obtained / total) * 100, 2) if total > 0 else 0

    if percentage >= 90:
        grade, remarks = 'O', 'Outstanding'
    elif percentage >= 80:
        grade, remarks = 'A+', 'Very Satisfactory'
    elif percentage >= 70:
        grade, remarks = 'A', 'Satisfactory'
    elif percentage >= 60:
        grade, remarks = 'B+', 'Fairly Satisfactory'
    elif percentage >= 50:
        grade, remarks = 'B', 'Passed'
    else:
        grade, remarks = 'Fail', 'Did Not Meet Expectations'

    report_data = {
        'student': student,
        'total_days': total_days,
        'attended_days': attended_days,
        'attendance_perc': attendance_perc,
        'eng': eng, 'urdu': urdu, 'math': math, 'phy': phy, 'cs': cs, 'prog': prog, 'db_sys': db_sys,
        'obtained': obtained, 'total': total,
        'percentage': percentage, 'grade': grade, 'remarks': remarks
    }
    return render_template('preview_report.html', data=report_data)

# ----------------- SAVE REPORT -----------------
@app.route('/save_report', methods=['POST'])
def save_report():
    new_report = ReportCard(
        student_id=request.form.get('student_id'),
        total_days=request.form.get('total_days'),
        attended_days=request.form.get('attended_days'),
        eng=request.form.get('eng'),
        urdu=request.form.get('urdu'),
        math=request.form.get('math'),
        phy=request.form.get('phy'),
        cs=request.form.get('cs'),
        prog=request.form.get('prog'),
        db_sys=request.form.get('db_sys'),
        obtained_marks=request.form.get('obtained_marks'),
        total_marks=request.form.get('total_marks'),
        percentage=request.form.get('percentage'),
        grade=request.form.get('grade'),
        remarks=request.form.get('remarks')
    )
    db.session.add(new_report)
    db.session.commit()
    return redirect(url_for('manage_students'))

# ----------------- STUDENT PROFILE -----------------
@app.route('/student/<int:id>')
def student_profile(id):
    student = Student.query.get_or_404(id)
    return render_template('student_profile.html', student=student)

# ----------------- JSON API -----------------
@app.route('/api/student/<int:id>')
def api_student(id):
    student = Student.query.get(id)
    if not student:
        return {'error': 'Student not found'}, 404

    reports = []
    for r in student.report_cards:
        reports.append({
            'id': r.id,
            'term_id': f'#TRM-{r.id}',
            'total_marks': r.total_marks,
            'obtained_marks': r.obtained_marks,
            'percentage': r.percentage,
            'grade': r.grade
        })

    return {
        'id': student.id,
        'name': student.name,
        'student_id_code': student.student_id_code,
        'role': student.role,
        'father_name': student.father_name or 'N/A',
        'username': student.username,
        'email': student.email or 'N/A',
        'contact': student.contact or 'N/A',
        'qualifications': student.qualifications or 'N/A',
        'reports': reports
    }

# ----------------- DELETE REPORT -----------------
@app.route('/delete_report/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    report = ReportCard.query.get_or_404(report_id)
    student_id = report.student_id
    db.session.delete(report)
    db.session.commit()
    return redirect(url_for('student_profile', id=student_id))

# ----------------- EDIT REPORT -----------------
@app.route('/edit_report/<int:report_id>', methods=['GET', 'POST'])
def edit_report(report_id):
    report = ReportCard.query.get_or_404(report_id)

    if request.method == 'POST':
        report.total_days = int(request.form.get('total_days') or 1)
        report.attended_days = int(request.form.get('attended_days') or 0)
        report.eng = int(request.form.get('eng') or 0)
        report.urdu = int(request.form.get('urdu') or 0)
        report.math = int(request.form.get('math') or 0)
        report.phy = int(request.form.get('phy') or 0)
        report.cs = int(request.form.get('cs') or 0)
        report.prog = int(request.form.get('prog') or 0)
        report.db_sys = int(request.form.get('db_sys') or 0)

        report.obtained_marks = (report.eng + report.urdu + report.math +
                                 report.phy + report.cs + report.prog + report.db_sys)
        report.total_marks = 700
        report.percentage = round((report.obtained_marks / report.total_marks) * 100, 2) if report.total_marks > 0 else 0

        if report.percentage >= 90:
            report.grade, report.remarks = 'O', 'Outstanding'
        elif report.percentage >= 80:
            report.grade, report.remarks = 'A+', 'Very Satisfactory'
        elif report.percentage >= 70:
            report.grade, report.remarks = 'A', 'Satisfactory'
        elif report.percentage >= 60:
            report.grade, report.remarks = 'B+', 'Fairly Satisfactory'
        elif report.percentage >= 50:
            report.grade, report.remarks = 'B', 'Passed'
        else:
            report.grade, report.remarks = 'Fail', 'Did Not Meet Expectations'

        db.session.commit()
        return redirect(url_for('student_profile', id=report.student_id))

    return render_template('edit_report.html', report=report)

# ----------------- ASSIGN GRADE -----------------
@app.route('/assign_grade/<int:student_id>', methods=['GET', 'POST'])
def assign_grade(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        subject = request.form.get('subject')
        marks = int(request.form.get('marks') or 0)
        grade_letter = request.form.get('grade_letter')

        new_grade = Grade(
            student_id=student.id,
            subject=subject,
            marks=marks,
            grade=grade_letter
        )
        db.session.add(new_grade)
        db.session.commit()
        return redirect(url_for('student_profile', id=student.id))

    return render_template('assign_grade.html', student=student)

# ----------------- SYSTEM ANALYSIS -----------------
@app.route('/analysis')
def analysis_dashboard():
    total_reports = ReportCard.query.count()
    if total_reports == 0:
        return render_template('analysis.html', empty=True)

    passed = ReportCard.query.filter(ReportCard.grade != 'Fail').count()
    failed = total_reports - passed
    pass_rate = round((passed / total_reports) * 100, 1)

    avg_percentage = db.session.query(func.avg(ReportCard.percentage)).scalar()
    avg_percentage = round(avg_percentage, 2) if avg_percentage else 0.0

    top_students = ReportCard.query.order_by(ReportCard.percentage.desc()).limit(3).all()

    return render_template('analysis.html',
                           empty=False,
                           total=total_reports,
                           passed=passed,
                           failed=failed,
                           pass_rate=pass_rate,
                           avg_perc=avg_percentage,
                           top_students=top_students)


@app.route('/debug')
def debug_view():
    # Sirf admin dekh sakta hai
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    import os
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')
    
    # DB file existence check (only for sqlite)
    file_exists = "N/A"
    if 'sqlite' in db_uri:
        db_path = db_uri.replace('sqlite:///', '')
        file_exists = os.path.exists(db_path)
    
    students_count = Student.query.count()
    teachers_count = Student.query.filter_by(role='teacher').count()
    reports_count = ReportCard.query.count()
    grades_count = Grade.query.count()
    
    last_students = Student.query.order_by(Student.id.desc()).limit(3).all()
    admin = Student.query.filter_by(username='admin').first()
    
    html = f"""
    <h2>🔍 Debug Dashboard</h2>
    <table border="1" cellpadding="10">
        <tr><td>DB URI</td><td>{db_uri}</td></tr>
        <tr><td>DB File Exists?</td><td>{file_exists}</td></tr>
        <tr><td>Total Students</td><td>{students_count}</td></tr>
        <tr><td>Total Teachers</td><td>{teachers_count}</td></tr>
        <tr><td>Total Reports</td><td>{reports_count}</td></tr>
        <tr><td>Total Grades</td><td>{grades_count}</td></tr>
        <tr><td>Admin Found?</td><td>{'Yes – ' + admin.name if admin else 'NO ❌'}</td></tr>
    </table>
    <h3>Last 3 Students</h3>
    <ul>
        {''.join(f'<li>{s.name} ({s.student_id_code})</li>' for s in last_students) if last_students else '<li>None</li>'}
    </ul>
    <p><a href="/">Go to Dashboard</a></p>
    """
    return html

if __name__ == '__main__':
    app.run(debug=True)