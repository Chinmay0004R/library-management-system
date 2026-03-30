@startuml

' =======================
' Admin
' =======================

class Admin {
  +id: int
  +username: String
  +password_hash: String
  +role: String
  +set_password(password: String): void
  +check_password(password: String): boolean
}

' =======================
' Member
' =======================

class Member {
  +id: int
  +member_id: String
  +name: String
  +email: String
  +phone: String
  +membership_type: String
  +join_date: DateTime
  +borrowed_books: String
  +student_id: String
  +department: String
  +year: String
  +penalties: int
  +add_borrowed_book(book_id: String): void
  +remove_borrowed_book(book_id: String): void
  +get_borrowed_books_list(): List
  +can_borrow(): boolean
}

' =======================
' Book
' =======================

class Book {
  +id: int
  +book_id: String
  +title: String
  +author: String
  +isbn: String
  +category: String
  +total_copies: int
  +available_copies: int
  +update_availability(): void
  +is_available(): boolean
  +get_borrowed_count(): int
}

' =======================
' Transaction
' =======================

class Transaction {
  +id: int
  +member_id: String
  +book_id: String
  +borrow_date: DateTime
  +return_date: DateTime
  +fine: float
}

' =======================
' Attendance
' =======================

class AttendanceRecord {
  +id: int
  +visitor_id: String
  +entry_time: DateTime
  +exit_time: DateTime
  +is_active: boolean
}

' =======================
' Relationships
' =======================

Admin "1" --> "0..*" Member : manages
Admin "1" --> "0..*" Book : manages
Admin "1" --> "0..*" Transaction : oversees

Member "1" --> "0..*" Transaction : performs
Book "1" --> "0..*" Transaction : involved in
Member "1" --> "0..*" AttendanceRecord : has

@enduml
