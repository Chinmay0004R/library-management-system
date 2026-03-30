# Library Management System

## Installation & Usage

Follow these steps to get the project up and running locally:

1. **Clone the repository**
   ```bash
   git clone https://github.com/Chinmay0004R/library-management.git
   cd library-management
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   # source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database (only once)**
   ```bash
   flask db init         # if migrations folder is not already created
   flask db migrate -m "Initial schema"
   flask db upgrade
   ```
   Alternatively the `run.py` helper script will create the venv and install requirements for you; simply run `python run.py`.

5. **Run the application**
   ```bash
   # either
   python run.py
   # or
   flask run
   ```
   The server will start at http://127.0.0.1:5000 by default.

6. **First-time login**
   An administrator account is created automatically if none exists.
   - **Username:** `admin`
   - **Password:** `admin123`
   Be sure to change the password after logging in.


## Project Title
Library Management System - A Web-Based Solution for Modern Libraries

## Project Report
A comprehensive web-based library management system developed using Flask framework that automates and streamlines library operations.

## Certificate
[To be added by the institution]

## Acknowledgment
I would like to express my sincere gratitude to [Your Guide's Name] for their guidance and support throughout this project. I also thank [Institution Name] for providing the necessary resources and infrastructure.

## Declaration
I hereby declare that this project work titled "Library Management System" is my genuine work carried out under the guidance of [Guide's Name] at [Institution Name]. This work has not been submitted elsewhere for any degree or diploma.

## Table of Contents

### 1. Introduction
The Library Management System is a modern solution designed to automate library operations, making it easier for librarians to manage books, members, and transactions efficiently. This system replaces traditional paper-based methods with a digital solution.

### 2. Background (Existing System)
Traditional library systems often rely on:
- Manual record-keeping of books and members
- Paper-based tracking of borrowing/returning
- Time-consuming book search and inventory management
- Manual attendance tracking
- Limited reporting capabilities

### 3. Objectives
- Automate library operations and reduce manual work
- Implement efficient book tracking and management
- Provide easy member management and authentication
- Enable quick book search and categorization
- Implement automated notification system
- Track library attendance digitally
- Generate comprehensive reports

### 4. Purpose
To create a modern, efficient, and user-friendly library management system that streamlines library operations and enhances user experience.

### 5. Scope
- User authentication and authorization
- Book management (add, delete, update)
- Member management
- Borrowing and returning processes
- Attendance tracking
- Automated notifications
- Report generation
- Data import/export capabilities

### 6. Sources & Technologies


#### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap
- Flask Templates (Jinja2)

#### Backend
- Python 3.x
- Flask Framework
- SQLAlchemy ORM
- SQLite Database
- Flask-Mail for notifications

### 7. System Analysis

#### Problem Definition
Traditional library systems face challenges with:
- Manual record keeping
- Book tracking
- Member management
- Attendance monitoring
- Report generation

#### Requirement Specification

**Functional Requirements:**
1. User Management
   - Admin authentication
   - User role management
   - Profile management

2. Book Management
   - Add/Edit/Delete books
   - Search and filter books
   - Track book status
   - Import books via CSV

3. Member Management
   - Add/Edit/Delete members
   - Track borrowed books
   - Manage member types
   - Import members via CSV

4. Transaction Management
   - Book borrowing
   - Book returning
   - Fine calculation
   - Transaction history

5. Attendance System
   - Check-in/Check-out
   - Attendance reports
   - Visitor tracking

**Non-Functional Requirements:**
- Security
- Performance
- Usability
- Reliability
- Maintainability

### 8. Gantt Chart
[Include your project timeline and milestones]

### 9. Existing System & Limitations
Current manual systems face limitations such as:
- Time-consuming processes
- Error-prone manual entry
- Difficult to track books
- No automated notifications
- Limited reporting capabilities
- Paper-based attendance tracking

### 10. Proposed System

#### Advantages
1. Automated Operations
2. Real-time Updates
3. Efficient Search
4. Automated Notifications
5. Digital Attendance Tracking
6. Comprehensive Reporting
7. Data Import/Export
8. User-friendly Interface

#### Limitations Overcome
1. Eliminated manual record keeping
2. Automated book tracking
3. Digital attendance system
4. Instant report generation
5. Automated notification system
6. Efficient data management

### 11. Technology Used

#### Hardware Requirements
- Processor: Intel Core i3 or higher
- RAM: 4GB minimum
- Storage: 10GB minimum
- Internet connectivity

#### Software Requirements
- Operating System: Windows/Linux/MacOS
- Python 3.x
- Flask Framework
- SQLite Database
- Modern Web Browser

#### Languages/Tools
- Python
- HTML/CSS/JavaScript
- SQLite
- Git
- Visual Studio Code
- Flask and its extensions

### 12. System Design

#### ERD
See the complete Entity Relationship Diagram in [ER Diagram](docs/diagrams/er_diagram.md)

#### Normalization
Database tables are normalized to 3NF to ensure data integrity and eliminate redundancy.

### 13. Data Design
The system uses SQLite database with the following main tables:
- Users
- Books
- Members
- AttendanceRecords
- Transactions

### 14. Diagrams

#### ER Diagram
See the detailed Entity Relationship Diagram in [ER Diagram](docs/diagrams/er_diagram.md)

#### Use Case Diagram
See the Use Case Diagram showing system interactions in [Use Case Diagram](docs/diagrams/use_case_diagram.md)

#### Data Flow Diagram (DFD)
See the Data Flow Diagram showing system data flow in [Data Flow Diagram](docs/diagrams/data_flow_diagram.md)

#### Class Diagram
See the Class Diagram showing system structure in [Class Diagram](docs/diagrams/class_diagram.md)

#### Object Diagram
See the Object Diagram showing system instances in [Object Diagram](docs/diagrams/object_diagram.md)

#### Activity Diagram
See the Activity Diagram showing the book borrowing process in [Activity Diagram](docs/diagrams/activity_diagram.md)

#### State Diagram
See the State Diagram showing book states in [State Diagram](docs/diagrams/state_diagram.md)

#### Deployment Diagram
See the Deployment Diagram showing system architecture in [Deployment Diagram](docs/diagrams/deployment_diagram.md)

### 15. Testing

#### Test Case Design
1. Unit Testing
   - Individual component testing
   - Function testing
   - Database operations testing

2. Integration Testing
   - Module integration testing
   - API testing
   - User flow testing

#### Testing Approaches
- Black Box Testing
- White Box Testing
- User Acceptance Testing

### 16. System Coding & Implementation
The system is implemented using:
- Flask framework for backend
- SQLAlchemy for database operations
- Jinja2 templates for frontend
- Bootstrap for responsive design
- Flask-Mail for email notifications

Key implementation files:
- app.py: Main application file
- models.py: Database models
- routes.py: URL routing
- templates/: HTML templates
- static/: CSS, JS, and image files

### 17. Deployment
Deployment steps:
1. System Requirements
2. Python Environment Setup
3. Database Configuration
4. Environment Variables
5. Running the Application
6. Maintenance Procedures

### 18. Conclusion
The Library Management System successfully achieves its objectives of automating library operations and providing an efficient solution for modern libraries. The system demonstrates significant improvements over traditional methods and provides a foundation for future enhancements.

### 19. References / Bibliography
1. Flask Documentation: https://flask.palletsprojects.com/
2. SQLAlchemy Documentation: https://www.sqlalchemy.org/
3. Bootstrap Documentation: https://getbootstrap.com/
4. Python Documentation: https://docs.python.org/
5. [Add more references as needed]