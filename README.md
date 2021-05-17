
Create a Library management system that allows the following features for a librarian and multiple users -

	- The librarian should be able to add/remove a book
	- The librarian Update the quanities of books
	- The librarian Issue/Deposit a book
	- The librarian generate a penalty if book is due for longer
	- The User can check and request for issue(Email should be triggered for issue request).
	- The librarian should be able to export a csv of all issues/deposits for a date range


Models : 

- Book
- IssueLog
- IssueRequest
- Custom User Model (to handle email)

Views:
    
    BookViewSet
        CRUD
        Search

    IssueRequestViewSet
        CRUD
        Search
        - custom perform_create
    
    Signal on post_save of IssueRequest

    IssueLogViewSet
        CRUD
        Search
        - custome perform_create

    Signal on post_save of IssueLog

    IssueLogExportView
        - get functionality

    
Project Completed.
Video Ends.