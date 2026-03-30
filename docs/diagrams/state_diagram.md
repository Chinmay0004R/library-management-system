@startuml
[*] --> Available : Add New Book

state Available {
    [*] --> InStock
    InStock --> Reserved : Place Hold
    Reserved --> InStock : Hold Expired
}

state Borrowed {
    [*] --> OnLoan
    OnLoan --> NearingDue : 3 Days Before Due
    NearingDue --> Overdue : Due Date Passed
    OnLoan --> Renewed : Extend Loan
    Renewed --> NearingDue : Near New Due Date
}

state Overdue {
    [*] --> PendingNotification
    PendingNotification --> NotificationSent : Send Reminder
    NotificationSent --> PenaltyApplied : After Grace Period
}

Available --> Borrowed : Checkout Book
Borrowed --> Available : Return Book
Borrowed --> Overdue : Due Date Passed
Overdue --> Available : Return Book + Pay Fine

Available --> UnderMaintenance : Repair/Maintain
UnderMaintenance --> Available : Maintenance Complete

Available --> Lost : Mark as Lost
Borrowed --> Lost : Report Lost
Lost --> Available : Replace Book

Available --> Removed : Remove from System
Removed --> [*]
@enduml
