from database import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id_code = db.Column(db.String(6), unique=True, nullable=True) 
    
    name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=True)
    
    role = db.Column(db.String(50), nullable=False, default='student')
    username = db.Column(db.String(50), nullable=False, unique=True)
    
    email = db.Column(db.String(100), unique=True, nullable=True)
    contact = db.Column(db.String(20), nullable=True)
    qualifications = db.Column(db.String(255), nullable=True)
    
    password = db.Column(db.String(255), nullable=False, default='admin123')
    
    # Relationships
    grades = db.relationship('Grade', backref='student', lazy=True, cascade="all, delete-orphan")
    report_cards = db.relationship('ReportCard', backref='student', lazy=True, cascade="all, delete-orphan")

# Purana 1-Subject table (Agar tu future mein single tests add karna chahay)
class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    grade_letter = db.Column(db.String(5), nullable=False)

# NAYA MASSIVE ENGINE TABLE
class ReportCard(db.Model):
    __tablename__ = 'report_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    
    total_days = db.Column(db.Integer, nullable=False)
    attended_days = db.Column(db.Integer, nullable=False)
    
    # 7 Subjects
    eng = db.Column(db.Integer)
    urdu = db.Column(db.Integer)
    math = db.Column(db.Integer)
    phy = db.Column(db.Integer)
    cs = db.Column(db.Integer)
    prog = db.Column(db.Integer)
    db_sys = db.Column(db.Integer)
    
    # Calculations
    obtained_marks = db.Column(db.Integer, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    remarks = db.Column(db.String(100), nullable=False)