from django.contrib import admin
from .models import Book, IssueLog, IssueRequest, User

admin.site.register(User)
admin.site.register(Book)
admin.site.register(IssueLog)
admin.site.register(IssueRequest)
