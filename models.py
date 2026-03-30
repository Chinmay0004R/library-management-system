from users import db
from datetime import datetime

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(30), nullable=False)
    category = db.Column(db.String(50), default='General')
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    # Relationship: borrowed_by (AttendanceRecord)

    @property
    def is_available(self):
        return self.available_copies > 0

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    membership_type = db.Column(db.String(20), default='Regular')
    role = db.Column(db.String(20), default='student')
    student_id = db.Column(db.String(30), nullable=True)
    department = db.Column(db.String(80), nullable=True)
    year = db.Column(db.String(10), nullable=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    penalties = db.Column(db.Integer, default=0)
    borrowed_books = db.Column(db.String, default='')
    # Relationship: attendance_records, borrowed_books (AttendanceRecord)

    @property
    def borrowed_books_list(self):
        if self.borrowed_books:
            return [b for b in self.borrowed_books.split(',') if b]
        return []

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)
    visitor_id = db.Column(db.String(50), nullable=True)  # For non-members
    name = db.Column(db.String(100), nullable=False)
    visitor_type = db.Column(db.String(20), nullable=False)  # 'member', 'visitor', 'staff'
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime, nullable=True)
    purpose = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    # Relationships
    member = db.relationship('Member', backref='attendance_records', lazy=True)
    book = db.relationship('Book', backref='attendance_records', lazy=True)

    @property
    def get_duration(self):
        """Return visit duration in minutes, or None if not checked out."""
        if self.exit_time and self.entry_time:
            return int((self.exit_time - self.entry_time).total_seconds() // 60)
        return None 