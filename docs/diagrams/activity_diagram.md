@startuml

[*] --> AdminLogin
AdminLogin --> DashboardView
DashboardView --> SelectOperation

SelectOperation --> BorrowBook
SelectOperation --> ReturnBook
SelectOperation --> ManageMembers
SelectOperation --> ManageBooks
SelectOperation --> TrackAttendance

state BorrowBook {

    [*] --> EnterMemberID
    EnterMemberID --> ValidateMember

    ValidateMember --> CheckMemberLimits : Valid Member
    ValidateMember --> ShowError : Invalid Member
    ShowError --> EnterMemberID

    CheckMemberLimits --> EnterBookID : Within Limits
    CheckMemberLimits --> ShowLimitError : Exceeds Limits
    ShowLimitError --> EnterMemberID

    EnterBookID --> ValidateBook
    ValidateBook --> CheckAvailability : Valid Book
    ValidateBook --> ShowError : Invalid Book

    CheckAvailability --> ProcessBorrow : Available
    CheckAvailability --> ShowNotAvailable : Not Available
    ShowNotAvailable --> EnterBookID

    ProcessBorrow --> UpdateDatabase
    UpdateDatabase --> SendEmailNotification
    SendEmailNotification --> UpdateMemberRecord
    UpdateMemberRecord --> [*]
}

state ReturnBook {

    [*] --> EnterReturnDetails
    EnterReturnDetails --> ValidateReturn

    ValidateReturn --> CalculateFine : Valid Return
    ValidateReturn --> ShowError : Invalid Return

    CalculateFine --> ProcessReturn : No Fine
    CalculateFine --> CollectFine : Has Fine
    CollectFine --> ProcessReturn

    ProcessReturn --> UpdateInventory
    UpdateInventory --> SendReturnNotification
    SendReturnNotification --> [*]
}

@enduml
