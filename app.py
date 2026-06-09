import os
import random
from flask import Flask, render_template, request, redirect, url_for, session
from database import db
from models import Student, Grade
from models import Student, Grade, ReportCard  # Nayi class yahan import hogi!
from sqlalchemy import func

app = Flask(__name__)

# Security Key for Sessions (Dynamic for strict logouts)
app.secret_key = os.urandom(24)

# MySQL Configuration (Tera Database Vault)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Root123@localhost/student_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ----------------- SECURITY ROUTES ----------------- 
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        form_username = request.form.get('username')
        form_password = request.form.get('password')
        
        user = Student.query.filter_by(username=form_username, password=form_password).first()
        
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            return redirect(url_for('index'))
        else:
            error = "Invalid Username or Password!"
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----------------- MAIN DASHBOARD ROUTE ----------------- 
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    total_students = Student.query.filter_by(role='student').count()
    total_teachers = Student.query.filter_by(role='teacher').count()
    
    # THE UPGRADE: Fetch latest 5 report cards generated, sorted by newest first
    recent_activities = ReportCard.query.order_by(ReportCard.id.desc()).limit(5).all()
    
    return render_template('index.html', 
                           student_count=total_students, 
                           teacher_count=total_teachers,
                           recent_activities=recent_activities)
@app.route('/students')
def manage_students():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    all_users = Student.query.all()
    return render_template('students.html', users=all_users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        form_name = request.form.get('name')
        form_role = request.form.get('role')
        form_username = request.form.get('username')
        form_father = request.form.get('father_name')
        form_email = request.form.get('email')
        form_contact = request.form.get('contact')
        form_qualifications = request.form.get('qualifications')
        
        # 6-Digit Auto-Generator Logic
        while True:
            generated_code = str(random.randint(100000, 999999))
            existing = Student.query.filter_by(student_id_code=generated_code).first()
            if not existing:
                break
        
        new_user = Student(
            student_id_code=generated_code,
            name=form_name, 
            father_name=form_father,
            role=form_role, 
            username=form_username, 
            email=form_email,
            contact=form_contact,
            qualifications=form_qualifications,
            password='admin123'
        )
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('manage_students'))
    
    return render_template('student_form.html')

# ----------------- AUTO-GRADING ENGINE ----------------- 
@app.route('/grading_dashboard')
def grading_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    all_students = Student.query.filter_by(role='student').all()
    return render_template('grading_form.html', students=all_students)

@app.route('/preview_report', methods=['POST'])
def preview_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    student_id = request.form.get('student_id')
    student = Student.query.get(student_id)
    
    # Safe Mode Attendance Calculation (Avoid Division by Zero)
    total_days = int(request.form.get('total_days') or 1)
    attended_days = int(request.form.get('attended_days') or 0)
    attendance_perc = round((attended_days / total_days) * 100, 2)
    
    # Safe Mode Marks Fetching (Empty inputs become 0)
    eng = int(request.form.get('eng') or 0)
    urdu = int(request.form.get('urdu') or 0)
    math = int(request.form.get('math') or 0)
    phy = int(request.form.get('phy') or 0)
    cs = int(request.form.get('cs') or 0)
    prog = int(request.form.get('prog') or 0)
    db_sys = int(request.form.get('db_sys') or 0)
    
    obtained_marks = eng + urdu + math + phy + cs + prog + db_sys
    total_marks = 700
    percentage = round((obtained_marks / total_marks) * 100, 2)
    
    # Strict Grading Logic
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
        'student': student, 'total_days': total_days, 'attended_days': attended_days, 'attendance_perc': attendance_perc,
        'eng': eng, 'urdu': urdu, 'math': math, 'phy': phy, 'cs': cs, 'prog': prog, 'db_sys': db_sys,
        'obtained': obtained_marks, 'total': total_marks,
        'percentage': percentage, 'grade': grade, 'remarks': remarks
    }
    
    return render_template('preview_report.html', data=report_data)


# ----------------- SAVE REPORT ENGINE ----------------- 
@app.route('/save_report', methods=['POST'])
def save_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Hidden form se saara data pakro aur naya record banao
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

    # Vault mein lock kar do
    db.session.add(new_report)
    db.session.commit()

    # Success ke baad wapis students list par bhej do
    return redirect(url_for('manage_students'))

# ----------------- STUDENT PROFILE ENGINE ----------------- 
@app.route('/student/<int:id>')
def student_profile(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # Database se specific student ko nikaalo
    student = Student.query.get_or_404(id)
    
    return render_template('student_profile.html', student=student)

# ----------------- DELETE REPORT ENGINE ----------------- 
@app.route('/delete_report/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # Database se woh specific report pakro
    report = ReportCard.query.get_or_404(report_id)
    
    # Delete karne se pehle student ki ID save kar lo, taake wapis usi ki profile par ja sakein
    student_id = report.student_id 
    
    # Vault se data hamesha ke liye khatam
    db.session.delete(report)
    db.session.commit()
    
    # Wapis usi student ki profile par redirect karo
    return redirect(url_for('student_profile', id=student_id))

# ----------------- EDIT REPORT ENGINE ----------------- 
@app.route('/edit_report/<int:report_id>', methods=['GET', 'POST'])
def edit_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # Database se purani report pakro
    report = ReportCard.query.get_or_404(report_id)
    
    if request.method == 'POST':
        # Naye values ko purani report mein override karo
        report.total_days = int(request.form.get('total_days') or 1)
        report.attended_days = int(request.form.get('attended_days') or 0)
        
        report.eng = int(request.form.get('eng') or 0)
        report.urdu = int(request.form.get('urdu') or 0)
        report.math = int(request.form.get('math') or 0)
        report.phy = int(request.form.get('phy') or 0)
        report.cs = int(request.form.get('cs') or 0)
        report.prog = int(request.form.get('prog') or 0)
        report.db_sys = int(request.form.get('db_sys') or 0)
        
        # Recalculate everything
        report.obtained_marks = report.eng + report.urdu + report.math + report.phy + report.cs + report.prog + report.db_sys
        report.total_marks = 700
        report.percentage = round((report.obtained_marks / report.total_marks) * 100, 2)
        
        # Re-apply strict grading logic
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
            
        # Vault lock (update existing record)
        db.session.commit()
        
        # Wapis usi student ki profile par redirect karo
        return redirect(url_for('student_profile', id=report.student_id))
        
    # Agar request GET hai, toh edit form dikhao purane data ke sath
    return render_template('edit_report.html', report=report)

# ----------------- SYSTEM ANALYSIS ENGINE ----------------- 
@app.route('/analysis')
def analysis_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    total_reports = ReportCard.query.count()
    
    # Agar database khali hai toh crash se bachne ka check
    if total_reports == 0:
        return render_template('analysis.html', empty=True)
        
    # 1. Pass/Fail Ratio
    passed = ReportCard.query.filter(ReportCard.grade != 'Fail').count()
    failed = total_reports - passed
    pass_rate = round((passed / total_reports) * 100, 1)
    
    # 2. Overall System Average
    avg_percentage = db.session.query(func.avg(ReportCard.percentage)).scalar()
    avg_percentage = round(avg_percentage, 2) if avg_percentage else 0.0
    
    # 3. Elite Leaderboard (Top 3 Highest Percentages)
    top_students = ReportCard.query.order_by(ReportCard.percentage.desc()).limit(3).all()
    
    return render_template('analysis.html', 
                           empty=False,
                           total=total_reports, 
                           passed=passed, 
                           failed=failed, 
                           pass_rate=pass_rate, 
                           avg_perc=avg_percentage, 
                           top_students=top_students)

if __name__ == '__main__':
    app.run(debug=True)