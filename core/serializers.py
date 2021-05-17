from rest_framework import serializers
from .models import Book, IssueLog, IssueRequest


class BookSerializer(serializers.Serializer):
    class Meta:
        model = Book
        fields = ['id', 'isbn', 'title', 'author', 'quantity', 'available']
        read_only_fields = ('id',)


class BookIssueRequestSerializer(serializers.Serializer):
    class Meta:
        model = IssueRequest
        fields = ['id', 'requested', 'book', 'request_status', 'request_date']
        read_only_fields = ('id',)


class BookIssueLogSerializer(serializers.Serializer):
    class Meta:
        model = IssueLog
        fields = ['id', 'borrower', 'book', 'issued_date', 'due_date', 'deposit_date', 'penalty']
        read_only_fields = ('id',)

