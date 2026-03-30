@startuml
left to right direction

' =======================
' External Entities
' =======================

rectangle "Admin" as Admin
rectangle "Member" as Member
rectangle "Email Server" as EmailServer

' =======================
' Data Stores
' =======================

database "User DB" as UserDB
database "Book DB" as BookDB
database "Transaction DB" as TransDB
database "Attendance DB" as AttendDB

' =======================
' Authentication
' =======================

rectangle "1.0 User Authentication" as P1
rectangle "1.1 Login Validation" as P11
rectangle "1.2 Session Management" as P12

Admin --> P1 : credentials
Member --> P1 : credentials
P1 --> P11
P11 --> UserDB : verify user
UserDB --> P11 : auth result
P11 --> P12 : valid user
P12 --> Admin : session created
P12 --> Member : session created

' =======================
' Book Management
' =======================

rectangle "2.0 Book Management" as P2
rectangle "2.1 Add / Update Books" as P21
rectangle "2.2 Import Books" as P22
rectangle "2.3 Search Books" as P23

Admin --> P2 : book details
P2 --> P21
P21 --> BookDB : save/update book
P22 --> BookDB : bulk import
P23 --> BookDB : search query
BookDB --> P23 : search results
P23 --> Admin : book list

' =======================
' Member Management
' =======================

rectangle "3.0 Member Management" as P3
rectangle "3.1 Add / Update Members" as P31
rectangle "3.2 Import Members" as P32
rectangle "3.3 Track Penalties" as P33

Admin --> P3 : member info
P3 --> P31
P31 --> UserDB : save/update member
P33 --> TransDB : fetch fines
TransDB --> P33 : fine data
P33 --> Admin : penalty status

' =======================
' Transaction Management
' =======================

rectangle "4.0 Transaction Processing" as P4
rectangle "4.1 Borrow Processing" as P41
rectangle "4.2 Return Processing" as P42
rectangle "4.3 Fine Calculation" as P43

Admin --> P4 : borrow/return request
P4 --> P41
P41 --> BookDB : check availability
BookDB --> P41 : availability
P41 --> TransDB : create transaction
P42 --> TransDB : close transaction
P42 --> BookDB : update copies
P43 --> TransDB : calculate fine
P43 --> Admin : fine amount

' =======================
' Attendance System
' =======================

rectangle "5.0 Attendance Tracking" as P5
rectangle "5.1 Check In" as P51
rectangle "5.2 Check Out" as P52
rectangle "5.3 Attendance Reports" as P53

Member --> P5 : entry/exit
P5 --> P51
P51 --> AttendDB : record entry
P52 --> AttendDB : record exit
P53 --> AttendDB : fetch attendance
AttendDB --> P53 : attendance data
P53 --> Admin : attendance report

' =======================
' Reporting
' =======================

rectangle "6.0 Report Generation" as P6

Admin --> P6 : report request
P6 --> BookDB
P6 --> TransDB
P6 --> AttendDB
P6 --> Admin : reports

' =======================
' Notifications
' =======================

TransDB --> EmailServer : due / fine notification

@enduml
