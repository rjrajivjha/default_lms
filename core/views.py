from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, permissions, views, filters
from rest_framework.exceptions import APIException
from .models import Book, IssueLog, IssueRequest
from .serializers import BookSerializer, BookIssueRequestSerializer, BookIssueLogSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.IsAdminUser]
    search_fields = ['title', 'isbn', 'author']
    filter_backends = (filters.SearchFilter,)


def check_book_not_issued_to_user(borrower, book):
    qs = IssueLog.objects.filter(book=book,borrower=borrower,deposit_date=None)
    if qs:
        return False
    return True


class IssueRequestViewSet(viewsets.ModelViewSet):
    queryset = IssueRequest.objects.all()
    serializer_class = BookIssueRequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.IsAdminUser]
    search_fields = ['requester', 'book', 'request_status', 'request_date']
    filter_backends = (filters.SearchFilter,)

    def perform_create(self, serializer):
        try:
            book = Book.objects.get(pk=self.request.data['book'])
        except ObjectDoesNotExist:
            raise APIException("Requested Book Does Not Exist")

        try:
            issue_request = IssueRequest.objects.get(
                book = self.request.data['book'], requester=self.request.data['requester'],
                request_status=IssueRequest.RequestStatus.Requested
            )
        except ObjectDoesNotExist:
            issue_request = None

        if issue_request:
            raise APIException("Book has already been requested")

        if book.available > 0 and book.quantity > 0 and\
                check_book_not_issued_to_user(self.request.data['requester'], self.request.data['book']):
            serializer.save()
        else:
            raise APIException("There was a problem while Requesting to issue this book. \n"
                               "Possible Reasons : "
                               "1. Either Book is not available"
                               "2. Book is already issued on your name")


def check_book_exist(book_id):
    try:
        book = Book.objects.get(pk=book_id)
    except ObjectDoesNotExist:
        raise APIException("Requested Book Does Not Exist")
    return book


class BookIssueLogViewSet(viewsets.ViewSet):
    queryset = IssueLog.objects.all()
    serializer_class = BookIssueLogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.IsAdminUser]
    search_fields = ['book__title', 'borrower__email', 'due_date', 'issued_date', 'deposit_date']
    filter_backends = (filters.SearchFilter,)
    http_method_names = ['get', 'post', 'put', 'patch', 'head']

    def perform_create(self, serializer):
        book = check_book_exist(self.request.data['book'])
        try:
            issue_request = IssueRequest.objects.get(
                book=self.request.data['book'], requester=self.request.data['borrower']
            )
        except ObjectDoesNotExist:
            issue_request = None
        if book.available > 0 and book.quantity > 0 and check_book_not_issued_to_user(
                self.request.data['borrower'], self.request.data['book']):
            book.available -= 1
            serializer.save()
            book.save()
            if issue_request and issue_request.request_status=='RQ':
                issue_request.request_status= IssueRequest.RequestStatus.Issued
                issue_request.save()
        else:
            raise APIException("There was a problem while Issuing this book to user. \n"
                               "Possible Reasons : "
                               "1. Either Book is not available"
                               "2. Book is already issued to user.")
