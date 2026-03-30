```mermaid
erDiagram
    USER {
        int id
        string username
        string password
        string role
        string department
        datetime created_at
    }

    MEMBER {
        string member_id
        string name
        string phone
        string memberships
        datetime join_date
        string student_net
        int penalties
        string borrowed_books
    }

    ATTENDANCE_RECORD {
        string visitor_id
        string name
        string purpose
        datetime entry_time
        datetime exit_time
        boolean is_active
    }

    TRANSACTION {
        int transaction_id
        string member_id
        string book_id
        datetime borrow_date
        datetime return_date
        float fine
    }

    BOOK {
        string book_id
        string title
        string author
        string isbn
        string category
        int total_copies
        int available_copies
        datetime added_date
    }

    USER ||--|| MEMBER : "is"
    MEMBER ||--o{ ATTENDANCE_RECORD : "has"
    MEMBER ||--o{ TRANSACTION : "performs"
    BOOK ||--o{ TRANSACTION : "involved in"