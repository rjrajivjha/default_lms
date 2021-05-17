from rest_framework import serializers
from .models import Book, IssueLog, IssueRequest


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'isbn', 'title', 'author', 'quantity', 'available']
        read_only_fields = ('id',)


class BookIssueLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueLog
        fields = ['id', 'book', 'borrower', 'issued_date', 'due_date', 'deposit_date', 'penalty']
        read_only_fields = ('id',)


class BookIssueRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueRequest
        fields = ['requestor', 'book', 'request_status', 'request_date']
        read_only_fields = ('id',)