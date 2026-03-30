@startuml ProcessFlow
title Process Flow - Login, Book Management, Reporting

actor Admin
participant System
database Database
participant EmailServer

== Login Flow ==
Admin -> System : Login Request
System -> Database : Validate Credentials
Database --> System : Validation Result
System --> Admin : Login Success / Failure

== Add Book Flow ==
Admin -> System : Add Book Details
System -> Database : Insert Book Record
Database --> System : Confirmation
System --> Admin : Book Added Successfully

== Issue Book Flow ==
Admin -> System : Issue Book to Member
System -> Database : Check Book Availability
Database --> System : Book Available
System -> Database : Update Book Status
System -> EmailServer : Send Notification to Member
EmailServer --> System : Notification Sent
System --> Admin : Book Issued Successfully

== Report Generation Flow ==
Admin -> System : Generate Report
System -> Database : Fetch Report Data
Database --> System : Report Data
System --> Admin : Display Report

== Member Registration Flow ==
Admin -> System : Register New Member
System -> Database : Insert Member Details
Database --> System : Confirmation
System --> Admin : Member Registered Successfully

@enduml
