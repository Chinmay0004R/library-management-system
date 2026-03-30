@startuml
left to right direction
skinparam packageStyle rectangle

actor Admin

package "Library Management System" {

  package "Authentication" {
    (Login)
  }

  package "Book Management" {
    (Add Book)
    (Update Book)
    (Delete Book)
    (Search Book)
    (Import Books)
  }

  package "Member Management" {
    (Add Member)
    (Update Member)
    (Delete Member)
    (Search Member)
    (Import Members)
  }

  package "Transaction Operations" {
    (Borrow Book)
    (Return Book)
    (Check Status)
    (Calculate Fine)
  }

  package "Attendance System" {
    (Check In)
    (Check Out)
    (View Attendance)
  }

  package "Reporting" {
    (View Reports)
  }

  package "User Management" {
    (Manage Users)
  }
}

Admin --> (Login)
Admin --> (Add Book)
Admin --> (Update Book)
Admin --> (Delete Book)
Admin --> (Search Book)
Admin --> (Import Books)

Admin --> (Add Member)
Admin --> (Update Member)
Admin --> (Delete Member)
Admin --> (Search Member)
Admin --> (Import Members)

Admin --> (Borrow Book)
Admin --> (Return Book)
Admin --> (Check Status)
Admin --> (Calculate Fine)

Admin --> (Check In)
Admin --> (Check Out)
Admin --> (View Attendance)

Admin --> (View Reports)
Admin --> (Manage Users)

@enduml
