from database import db


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100))
    role = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False, default='admin123')
    email = db.Column(db.String(120))
    contact = db.Column(db.String(20))
    qualifications = db.Column(db.String(200))

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    marks = db.Column(db.Integer, nullable=False)

class ReportCard(db.Model):
    # ... saare columns ...
    student = db.relationship('Student', backref='report_cards')
    __tablename__ = 'report_cards'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    total_days = db.Column(db.Integer, default=0)
    attended_days = db.Column(db.Integer, default=0)
    eng = db.Column(db.Integer, default=0)
    urdu = db.Column(db.Integer, default=0)
    math = db.Column(db.Integer, default=0)
    phy = db.Column(db.Integer, default=0)
    cs = db.Column(db.Integer, default=0)
    prog = db.Column(db.Integer, default=0)
    db_sys = db.Column(db.Integer, default=0)
    obtained_marks = db.Column(db.Integer, default=0)
    total_marks = db.Column(db.Integer, default=700)
    percentage = db.Column(db.Float, default=0.0)
    grade = db.Column(db.String(10))
    remarks = db.Column(db.String(100))
    

    # ✅ YEH LINE ADD KARO – Relationship back to Student
    student = db.relationship('Student', backref='report_cards')

    