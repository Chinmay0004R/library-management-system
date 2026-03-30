from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from users import db, User, create_initial_admin
from library import Library
from datetime import datetime, date, timedelta, time
import os
from functools import wraps
from flask_migrate import Migrate  
import csv
from io import TextIOWrapper
from apscheduler.schedulers.background import BackgroundScheduler
from models import Book, Member, AttendanceRecord
from sqlalchemy import and_, func
import pytz
from flask_mail import Mail, Message 
from config import get_config

app = Flask(__name__)
config = get_config()
app.config.from_object(config)

db.init_app(app)
mail = Mail(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)  # Added for migrations

with app.app_context():
    db.create_all()
    create_initial_admin(db)

# Initialize the main Library object
the_library = Library(mail=mail, app=app)

LOCAL_TZ = pytz.timezone('Asia/Kolkata')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Protect main features (books, members, attendance, borrow, return)
@app.route('/')
@login_required
def home():
    stats = {
        'total_books': Book.query.count(),
        'total_copies': db.session.query(func.sum(Book.total_copies)).scalar() or 0,
        'available_copies': db.session.query(func.sum(Book.available_copies)).scalar() or 0,
        'borrowed_copies': (db.session.query(func.sum(Book.total_copies)).scalar() or 0) - (db.session.query(func.sum(Book.available_copies)).scalar() or 0),
        'total_members': Member.query.count()
    }
    return render_template('home.html', stats=stats)

# --- Book Management ---
@app.route('/books')
@login_required
def books():
    books = Book.query.all()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        category = request.form.get('category', 'General')
        copies = int(request.form.get('copies', 1))
        # Check if book_id already exists
        if Book.query.filter_by(book_id=book_id).first():
            flash('Book ID already exists.', 'danger')
        else:
            book = Book(book_id=book_id, title=title, author=author, isbn=isbn, category=category, total_copies=copies, available_copies=copies)
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('books'))
    return render_template('add_book.html')

@app.route('/delete_book/<book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.filter_by(book_id=book_id).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully!', 'success')
    else:
        flash('Failed to delete book. Book may not exist.', 'danger')
    return redirect(url_for('books'))

# --- Member Management ---
@app.route('/members')
@login_required
def members():
    members = Member.query.all()
    return render_template('members.html', members=members)

@app.route('/add_member', methods=['GET', 'POST'])
@admin_required
def add_member():
    if request.method == 'POST':
        role = request.form.get('role', 'student')
        member_id = request.form['member_id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        student_id = request.form.get('student_id') if role == 'student' else None
        department = request.form.get('department') if role == 'student' else None
        year = request.form.get('year') if role == 'student' else None
        # Check if member_id already exists
        if Member.query.filter_by(member_id=member_id).first():
            flash('Member ID already exists.', 'danger')
        else:
            member = Member(member_id=member_id, name=name, email=email, phone=phone, membership_type=request.form.get('membership_type', 'Regular'), role=role, student_id=student_id, department=department, year=year)
            db.session.add(member)
            db.session.commit()
            flash('Member added successfully!', 'success')
            return redirect(url_for('members'))
    return render_template('add_member.html')

@app.route('/delete_member/<member_id>', methods=['POST'])
@admin_required
def delete_member(member_id):
    member = Member.query.filter_by(member_id=member_id).first()
    if member:
        db.session.delete(member)
        db.session.commit()
        flash('Member deleted successfully!', 'success')
    else:
        flash('Failed to delete member. Member may not exist.', 'danger')
    return redirect(url_for('members'))

# --- Borrow/Return Books ---
@app.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        member = Member.query.filter_by(member_id=member_id).first()
        book = Book.query.filter_by(book_id=book_id).first()
        if not member or not book:
            flash('Invalid member or book.', 'danger')
        elif book.available_copies < 1:
            flash('Book is not available.', 'danger')
        else:
            borrowed_books = getattr(member, 'borrowed_books', '')
            borrowed_list = borrowed_books.split(',') if borrowed_books else []
            if book_id in borrowed_list:
                flash('Member already borrowed this book.', 'danger')
            else:
                borrowed_list.append(book_id)
                member.borrowed_books = ','.join(borrowed_list)
                book.available_copies -= 1
                db.session.commit()
                flash('Book borrowed successfully!', 'success')
                
                # --- Send borrow notification ---
                if member.email:
                    try:
                        msg = Message(
                            subject="Library Notification: Book Borrowed",
                            sender=("Library", app.config['MAIL_USERNAME']),  # Updated line
                            recipients=[member.email],
                            body=f"Dear {member.name},\n\nYou have borrowed '{book.title}'.\n\nThank you,\nLibrary"
                        )
                        mail.send(msg)
                    except Exception as e:
                        print(f"Email notification failed for {member.email}: {str(e)}")
                        # Continue without failing - book is still borrowed successfully
        return redirect(url_for('books'))
    members = Member.query.all()
    books = Book.query.filter(Book.available_copies > 0).all()
    return render_template('borrow.html', members=members, books=books)

@app.route('/return', methods=['GET', 'POST'])
@login_required
def return_book():
    members = Member.query.all()
    books = Book.query.all()
    member_books = {}
    for member in members:
        borrowed_books = member.borrowed_books.split(',') if member.borrowed_books else []
        member_books[member.member_id] = [
            {'book_id': book.book_id, 'title': book.title}
            for book in books if book.book_id in borrowed_books
        ]
    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        member = Member.query.filter_by(member_id=member_id).first()
        book = Book.query.filter_by(book_id=book_id).first()
        if not member or not book:
            flash('Invalid member or book.', 'danger')
        else:
            borrowed_books = getattr(member, 'borrowed_books', '')
            borrowed_list = borrowed_books.split(',') if borrowed_books else []
            if book_id not in borrowed_list:
                flash('Book not borrowed by this member.', 'danger')
            else:
                borrowed_list.remove(book_id)
                member.borrowed_books = ','.join(borrowed_list)
                book.available_copies += 1
                db.session.commit()
                flash('Book returned successfully!', 'success')
                
                # --- Send return notification ---
                if member.email:
                    try:
                        msg = Message(
                            subject="Library Notification: Book Returned",
                            sender=("Library", app.config['MAIL_USERNAME']),  # Updated line
                            recipients=[member.email],
                            body=f"Dear {member.name},\n\nYou have returned '{book.title}'.\n\nThank you,\nLibrary"
                        )
                        mail.send(msg)
                    except Exception as e:
                        print(f"Email notification failed for {member.email}: {str(e)}")
                        # Continue without failing - book is still returned successfully
        return redirect(url_for('books'))
    return render_template('return.html', members=members, member_books=member_books)

# --- Attendance Management ---
@app.route('/attendance')
@login_required
def attendance():
    today = date.today()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)
    # Get today's stats
    total = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start_of_day, AttendanceRecord.entry_time <= end_of_day).count()
    students = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start_of_day, AttendanceRecord.entry_time <= end_of_day, AttendanceRecord.visitor_type == 'student').count()
    visitors_count = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start_of_day, AttendanceRecord.entry_time <= end_of_day, AttendanceRecord.visitor_type == 'visitor').count()
    staff = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start_of_day, AttendanceRecord.entry_time <= end_of_day, AttendanceRecord.visitor_type == 'staff').count()
    stats = {'total_visitors': total, 'members': students, 'visitors': visitors_count, 'staff': staff}
    current_visitors = AttendanceRecord.query.filter_by(is_active=True).all()
    # Attach member info for students/staff and convert entry_time to local timezone
    visitor_list = []
    for v in current_visitors:
        # Always treat as UTC, then convert to IST
        utc_entry_time = v.entry_time.replace(tzinfo=pytz.utc) if v.entry_time.tzinfo is None else v.entry_time.astimezone(pytz.utc)
        local_entry_time = utc_entry_time.astimezone(LOCAL_TZ)
        info = {'id': v.visitor_id, 'type': v.visitor_type, 'entry_time': local_entry_time, 'raw': v}
        if v.visitor_type in ['student', 'staff']:
            member = Member.query.filter_by(member_id=v.visitor_id).first()
            info['name'] = member.name if member else ''
        else:
            info['name'] = v.name
        visitor_list.append(info)
    return render_template('attendance.html', stats=stats, visitors=visitor_list)

@app.route('/check_in', methods=['GET', 'POST'])
@login_required
def check_in():
    if request.method == 'POST':
        visitor_type = request.form['visitor_type']
        visitor_id = request.form['visitor_id']
        name = request.form['name']
        purpose = request.form.get('purpose', '')
        # If it's a student or staff, get the name from the Member table
        if visitor_type in ['student', 'staff']:
            member = Member.query.filter_by(member_id=visitor_id).first()
            if member:
                name = member.name
        # Only allow check-in if not already active
        already_in = AttendanceRecord.query.filter_by(visitor_id=visitor_id, is_active=True).first()
        if already_in:
            flash('Check-in failed. Already checked in.', 'danger')
        else:
            record = AttendanceRecord(visitor_id=visitor_id, name=name, visitor_type=visitor_type, purpose=purpose, is_active=True, entry_time=datetime.utcnow())
            db.session.add(record)
            db.session.commit()
            flash('Check-in successful!', 'success')
        return redirect(url_for('attendance'))
    return render_template('check_in.html')

@app.route('/check_out', methods=['POST'])
@login_required
def check_out():
    visitor_id = request.form['visitor_id']
    record = AttendanceRecord.query.filter_by(visitor_id=visitor_id, is_active=True).first()
    if record:
        from datetime import datetime
        record.exit_time = datetime.now()
        record.is_active = False
        db.session.commit()
        flash('Check-out successful!', 'success')
    else:
        flash('Check-out failed. Not found or already checked out.', 'danger')
    return redirect(url_for('attendance'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.role != 'admin':
                flash('Only admins are allowed to log in.', 'danger')
                return render_template('login.html')
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/users')
@admin_required
def users():
    user_list = User.query.all()
    return render_template('users.html', users=user_list)

@app.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        student_id = request.form.get('student_id')
        department = request.form.get('department')
        year = request.form.get('year')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        elif role == 'student' and student_id and User.query.filter_by(student_id=student_id).first():
            flash('Student ID already registered.', 'danger')
        else:
            new_user = User(username=username, role=role)
            new_user.set_password(password)
            if role == 'student':
                new_user.student_id = student_id
                new_user.department = department
                new_user.year = year
            db.session.add(new_user)
            db.session.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('users'))
    return render_template('add_user.html')

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == session.get('username'):
        flash('You cannot delete your own account.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    return redirect(url_for('users'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    flash('Registration is disabled. Only admins can have accounts.', 'warning')
    return redirect(url_for('login'))

@app.route('/import_students', methods=['GET', 'POST'])
@admin_required
def import_students():
    results = []
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'danger')
            return render_template('import_students.html', results=results)
        stream = TextIOWrapper(file.stream, encoding='utf-8')
        reader = csv.DictReader(stream)
        required_fields = {'username', 'password', 'student_id'}
        if not required_fields.issubset(reader.fieldnames):
            flash('CSV format is wrong. Required columns: username, password, student_id.', 'danger')
            return render_template('import_students.html', results=results)
        for row in reader:
            username = row.get('username')
            password = row.get('password')
            student_id = row.get('student_id')
            department = row.get('department')
            year = row.get('year')
            if not username or not password or not student_id:
                results.append({'username': username, 'student_id': student_id, 'status': 'Missing required fields'})
                continue
            if User.query.filter_by(username=username).first():
                results.append({'username': username, 'student_id': student_id, 'status': 'Username exists'})
                continue
            if User.query.filter_by(student_id=student_id).first():
                results.append({'username': username, 'student_id': student_id, 'status': 'Student ID exists'})
                continue
            new_user = User(username=username, role='student', student_id=student_id, department=department, year=year)
            new_user.set_password(password)
            db.session.add(new_user)
            results.append({'username': username, 'student_id': student_id, 'status': 'Imported'})
        db.session.commit()
        flash('Import completed.', 'success')
    return render_template('import_students.html', results=results)

@app.route('/import_books', methods=['GET', 'POST'])
@admin_required
def import_books():
    results = []
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'danger')
            return render_template('import_books.html', results=results)
        stream = TextIOWrapper(file.stream, encoding='utf-8')
        reader = csv.DictReader(stream)
        required_fields = {'book_id', 'title', 'author', 'isbn'}
        if not required_fields.issubset(reader.fieldnames):
            flash('CSV format is wrong. Required columns: book_id, title, author, isbn.', 'danger')
            return render_template('import_books.html', results=results)
        for row in reader:
            book_id = row.get('book_id')
            title = row.get('title')
            author = row.get('author')
            isbn = row.get('isbn')
            category = row.get('category', 'General')
            copies = row.get('copies', 1)
            try:
                copies = int(copies)
            except Exception:
                copies = 1
            if not book_id or not title or not author or not isbn:
                results.append({'book_id': book_id, 'title': title, 'status': 'Missing required fields'})
                continue
            if Book.query.filter_by(book_id=book_id).first():
                results.append({'book_id': book_id, 'title': title, 'status': 'Book ID exists'})
                continue
            book = Book(book_id=book_id, title=title, author=author, isbn=isbn, category=category, total_copies=copies, available_copies=copies)
            db.session.add(book)
            results.append({'book_id': book_id, 'title': title, 'status': 'Imported'})
        db.session.commit()
        flash('Import completed.', 'success')
    return render_template('import_books.html', results=results)

@app.route('/admin/data_management')
@admin_required
def admin_data_management():
    return render_template('admin/data_management.html')

@app.route('/admin/users_data')
@admin_required
def admin_users_data():
    """Admin view of all users data."""
    users = User.query.all()
    user_stats = {
        'total': len(users),
        'admins': len([u for u in users if u.role == 'admin']),
        'students': len([u for u in users if u.role == 'student']),
        'staff': len([u for u in users if u.role == 'user'])
    }
    return render_template('admin/users_data.html', users=users, stats=user_stats)

@app.route('/admin/books_data')
@admin_required
def admin_books_data():
    """Admin view of all books data."""
    books = Book.query.all()
    book_stats = {
        'total_books': len(books),
        'total_copies': sum(book.total_copies for book in books),
        'available_copies': sum(book.available_copies for book in books),
        'borrowed_copies': sum(book.total_copies - book.available_copies for book in books),
        'categories': len(set(book.category for book in books))
    }
    return render_template('admin/books_data.html', books=books, stats=book_stats)

@app.route('/admin/members_data')
@admin_required
def admin_members_data():
    """Admin view of all members data."""
    members = Member.query.all()
    member_stats = {
        'total_members': len(members),
        'active_members': len([m for m in members if m.borrowed_books]),
        'premium_members': len([m for m in members if m.membership_type == 'Premium']),
        'regular_members': len([m for m in members if m.membership_type == 'Regular'])
    }
    return render_template('admin/members_data.html', members=members, stats=member_stats)

@app.route('/admin/attendance_data')
@admin_required
def admin_attendance_data():
    """Admin view of attendance data (database-backed)."""
    from models import AttendanceRecord
    from datetime import datetime, time, timedelta
    today = date.today()
    # Current visitors (checked in, not checked out)
    current_visitors = AttendanceRecord.query.filter_by(is_active=True).all()
    # Today's stats
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)
    total = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start_of_day, AttendanceRecord.entry_time <= end_of_day).count()
    students = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start_of_day, AttendanceRecord.entry_time <= end_of_day, AttendanceRecord.visitor_type == 'student').count()
    visitors_count = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start_of_day, AttendanceRecord.entry_time <= end_of_day, AttendanceRecord.visitor_type == 'visitor').count()
    staff = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start_of_day, AttendanceRecord.entry_time <= end_of_day, AttendanceRecord.visitor_type == 'staff').count()
    daily_stats = {'total_visitors': total, 'members': students, 'visitors': visitors_count, 'staff': staff}
    # Attendance history for last 7 days
    attendance_history = []
    for i in range(7):
        check_date = today - timedelta(days=i)
        start = datetime.combine(check_date, time.min)
        end = datetime.combine(check_date, time.max)
        day_total = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start, AttendanceRecord.entry_time <= end).count()
        day_students = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start, AttendanceRecord.entry_time <= end, AttendanceRecord.visitor_type == 'student').count()
        day_visitors = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start, AttendanceRecord.entry_time <= end, AttendanceRecord.visitor_type == 'visitor').count()
        day_staff = AttendanceRecord.query.filter(AttendanceRecord.entry_time >= start, AttendanceRecord.entry_time <= end, AttendanceRecord.visitor_type == 'staff').count()
        attendance_history.append({
            'date': check_date,
            'stats': {
                'total_visitors': day_total,
                'members': day_students,
                'visitors': day_visitors,
                'staff': day_staff
            }
        })
    return render_template('admin/attendance_data.html', 
                         current_visitors=current_visitors,
                         daily_stats=daily_stats,
                         attendance_history=attendance_history)

@app.route('/admin/transactions_data')
@admin_required
def admin_transactions_data():
    """Admin view of transaction history."""
    transactions = the_library.get_transaction_history(100)  # Last 100 transactions
    return render_template('admin/transactions_data.html', transactions=transactions)

@app.route('/admin/overdue_data')
@admin_required
def admin_overdue_data():
    """Admin view of overdue books."""
    overdue_books = the_library.get_overdue_books(14)  # Books overdue for 14+ days
    return render_template('admin/overdue_data.html', overdue_books=overdue_books)

@app.route('/admin/export_data/<data_type>')
@admin_required
def admin_export_data(data_type):
    """Export data as CSV."""
    from io import StringIO
    import csv
    
    output = StringIO()
    writer = csv.writer(output)
    
    if data_type == 'users':
        users = User.query.all()
        writer.writerow(['ID', 'Username', 'Role', 'Student ID', 'Department', 'Year'])
        for user in users:
            writer.writerow([user.id, user.username, user.role, user.student_id, user.department, user.year])
    
    elif data_type == 'books':
        books = Book.query.all()
        writer.writerow(['Book ID', 'Title', 'Author', 'ISBN', 'Category', 'Total Copies', 'Available Copies'])
        for book in books:
            writer.writerow([book.book_id, book.title, book.author, book.isbn, book.category, book.total_copies, book.available_copies])
    
    elif data_type == 'members':
        members = Member.query.all()
        writer.writerow(['Member ID', 'Name', 'Email', 'Phone', 'Membership Type', 'Join Date', 'Borrowed Books'])
        for member in members:
            writer.writerow([member.member_id, member.name, member.email, member.phone, member.membership_type, member.join_date, len(member.borrowed_books)])
    
    elif data_type == 'attendance':
        # Export today's attendance
        today = date.today()
        attendance_records = the_library.attendance_tracker.get_daily_attendance(today)
        writer.writerow(['Visitor ID', 'Name', 'Type', 'Entry Time', 'Exit Time', 'Duration (min)', 'Purpose'])
        for record in attendance_records:
            writer.writerow([record.visitor_id, record.name, record.visitor_type.value, 
                           record.entry_time, record.exit_time, record.get_duration(), record.purpose])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={data_type}_data_{date.today()}.csv'}
    )

@app.route('/admin/search_data', methods=['GET', 'POST'])
@admin_required
def admin_search_data():
    """Advanced search functionality for admin."""
    results = {}
    search_query = request.form.get('search_query', '')
    search_type = request.form.get('search_type', 'all')
    
    if request.method == 'POST' and search_query:
        if search_type in ['all', 'users']:
            users = User.query.filter(
                (User.username.contains(search_query)) |
                (User.student_id.contains(search_query)) |
                (User.department.contains(search_query))
            ).all()
            results['users'] = users
        
        if search_type in ['all', 'books']:
            books = Book.query.filter(
                (Book.title.contains(search_query)) |
                (Book.author.contains(search_query)) |
                (Book.isbn.contains(search_query))
            ).all()
            results['books'] = books
        
        if search_type in ['all', 'members']:
            members = Member.query.filter(
                (Member.name.contains(search_query)) |
                (Member.email.contains(search_query)) |
                (Member.member_id.contains(search_query))
            ).all()
            results['members'] = members
    
    return render_template('admin/search_data.html', results=results, search_query=search_query, search_type=search_type)

@app.route('/mark_book_lost/<member_id>/<book_id>', methods=['POST'])
@admin_required
def mark_book_lost(member_id, book_id):
    if the_library.mark_book_lost(member_id, book_id):
        flash('Book marked as lost and penalty applied.', 'warning')
    else:
        flash('Failed to mark book as lost.', 'danger')
    return redirect(url_for('members'))

@app.route('/apply_manual_penalty/<member_id>', methods=['POST'])
@admin_required
def apply_manual_penalty(member_id):
    """Manually apply a penalty to a member."""
    member = Member.query.filter_by(member_id=member_id).first()
    if not member:
        flash('Member not found.', 'danger')
        return redirect(url_for('members'))
    
    try:
        penalty_amount = int(request.form.get('penalty_amount', 0))
        reason = request.form.get('reason', 'Manual penalty')
        
        if penalty_amount <= 0:
            flash('Penalty amount must be greater than 0.', 'warning')
        else:
            member.penalties += penalty_amount
            db.session.commit()
            flash(f'Penalty of {penalty_amount} applied to {member.name}.', 'success')
            
            # Send email notification
            try:
                msg = Message(
                    subject="Library Penalty Notification",
                    sender=("Library", app.config['MAIL_USERNAME']),
                    recipients=[member.email],
                    body=f"""Dear {member.name},

A penalty of {penalty_amount} units has been applied to your account.

Reason: {reason}

Please contact the library if you have any questions.

Thank you,
Library"""
                )
                mail.send(msg)
            except Exception as e:
                print(f"Email notification failed for {member.email}: {str(e)}")
    except ValueError:
        flash('Invalid penalty amount.', 'danger')
    except Exception as e:
        flash(f'Error applying penalty: {str(e)}', 'danger')
    
    return redirect(url_for('members'))

@app.route('/clear_penalty/<member_id>', methods=['POST'])
@admin_required
def clear_penalty(member_id):
    """Clear/Remove penalty for a member."""
    member = Member.query.filter_by(member_id=member_id).first()
    if not member:
        flash('Member not found.', 'danger')
        return redirect(url_for('members'))
    
    try:
        old_penalty = member.penalties
        member.penalties = 0
        db.session.commit()
        flash(f'Penalty of {old_penalty} cleared for {member.name}.', 'success')
        
        # Send confirmation email
        try:
            msg = Message(
                subject="Library Penalty Cleared",
                sender=("Library", app.config['MAIL_USERNAME']),
                recipients=[member.email],
                body=f"""Dear {member.name},

Your library penalty has been cleared. You can now borrow books without restrictions.

Thank you,
Library"""
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email notification failed for {member.email}: {str(e)}")
    except Exception as e:
        flash(f'Error clearing penalty: {str(e)}', 'danger')
    
    return redirect(url_for('members'))

@app.route('/reduce_penalty/<member_id>', methods=['POST'])
@admin_required
def reduce_penalty(member_id):
    """Reduce a member's penalty by a specified amount."""
    member = Member.query.filter_by(member_id=member_id).first()
    if not member:
        flash('Member not found.', 'danger')
        return redirect(url_for('members'))
    
    try:
        amount = int(request.form.get('reduce_amount', 0))
        reason = request.form.get('reason', 'Partial penalty reduction')
        
        if amount <= 0:
            flash('Reduction amount must be greater than 0.', 'warning')
        elif member.penalties < amount:
            flash(f'Cannot reduce more than the current penalty ({member.penalties}).', 'warning')
        else:
            member.penalties -= amount
            db.session.commit()
            flash(f'Penalty reduced by {amount} for {member.name}.', 'success')
    except ValueError:
        flash('Invalid reduction amount.', 'danger')
    except Exception as e:
        flash(f'Error reducing penalty: {str(e)}', 'danger')
    
    return redirect(url_for('members'))

@app.route('/admin/penalties')
@admin_required
def admin_penalties():
    """Admin view of all members with penalties."""
    members_with_penalties = Member.query.filter(Member.penalties > 0).all()
    total_penalties = sum(m.penalties for m in members_with_penalties)
    
    penalty_stats = {
        'total_members_with_penalties': len(members_with_penalties),
        'total_penalties_amount': total_penalties,
        'average_penalty': total_penalties / len(members_with_penalties) if members_with_penalties else 0
    }
    
    return render_template('admin/penalties_data.html', 
                         members=members_with_penalties, 
                         stats=penalty_stats)

@app.route('/get_member_info/<member_id>')
@login_required
def get_member_info(member_id):
    member = Member.query.filter_by(member_id=member_id).first()
    if member:
        return jsonify({
            'name': member.name,
            'email': member.email,
            'phone': member.phone,
            'role': member.role,
            'department': member.department,
            'year': member.year
        })
    return jsonify({}), 404

@app.route('/admin/attendance_day/<date>')
@admin_required
def admin_attendance_day_detail(date):
    from datetime import datetime, time
    try:
        day = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('admin_attendance_data'))
    start = datetime.combine(day, time.min)
    end = datetime.combine(day, time.max)
    records = AttendanceRecord.query.filter(
        AttendanceRecord.entry_time >= start,
        AttendanceRecord.entry_time <= end
    ).order_by(AttendanceRecord.entry_time).all()
    return render_template('admin/attendance_day_detail.html', records=records, day=day)

def daily_tasks():
    the_library.send_early_return_reminders()
    the_library.send_overdue_reminders()
    the_library.apply_penalties()

scheduler = BackgroundScheduler()
scheduler.add_job(daily_tasks, 'interval', days=1)
scheduler.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

# Migration commands (run in terminal):
# flask db init         # Only once, to initialize migrations
# flask db migrate -m "Describe changes"
# flask db upgrade