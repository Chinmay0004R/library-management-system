@startuml
left to right direction
skinparam componentStyle rectangle

' =======================
' Client Layer
' =======================

package "Client Layer" {
  component "Web Browser" as Browser
  component "Static CSS Files" as CSS
  component "Static JS Files" as JS
  component "Static Images" as Images
}

' =======================
' Application Server
' =======================

package "Application Server" {
  component "Flask Web Server" as WebServer
  component "Application Logic" as AppLogic
  component "SQLAlchemy ORM" as ORM
  component "APScheduler\n(Background Scheduler)" as Scheduler
  component "Flask-Mail" as Mail
  component "Flask-Migrate" as Migrate
  component "Jinja2 Templates" as Templates
}

' =======================
' Database Server
' =======================

package "Database Server" {
  database "SQLite Database" as DB
  database "Migration Scripts" as Migrations
}

' =======================
' Email Server
' =======================

package "Email Server" {
  component "Gmail SMTP Server" as SMTP
}

' =======================
' Interactions
' =======================

Browser <--> WebServer
Browser --> CSS
Browser --> JS
Browser --> Images

WebServer <--> AppLogic
AppLogic <--> Templates
AppLogic <--> ORM
ORM <--> DB

Migrate <--> Migrations
Migrations <--> DB

Scheduler --> AppLogic
AppLogic <--> Mail
Mail <--> SMTP

@enduml
