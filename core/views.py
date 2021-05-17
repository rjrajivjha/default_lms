import csv
from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

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
    qs = IssueLog.objects.filter(book=book, borrower=borrower, deposit_date=None)
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
            raise APIException("Requested Book Does Not Exist.")

        try:
            issue_request = IssueRequest.objects.get(
                book=self.request.data['book'], requester=self.request.data['requester'],
                request_status=IssueRequest.RequestStatus.Requested)
        except ObjectDoesNotExist:
            issue_request = None

        if issue_request:
            raise APIException("Book has already been requested.")

        if book.available > 0 and book.quantity > 0 and\
                check_book_not_issued_to_user(self.request.data['requester'], self.request.data['book']):
            serializer.save()
        else:
            raise APIException("There was a problem while Requesting to Issue this book. \n "
                               "Possible Reasons : "
                               "1. Either Book is not available. "
                               "2. Book is already issued to user.")


class BookIssueLogViewSet(viewsets.ModelViewSet):
    """
    Deleting a Issue Log is not allowed.
    """
    queryset = IssueLog.objects.all()
    serializer_class = BookIssueLogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.IsAdminUser]
    search_fields = ['book__title', 'borrower__email', 'issued_date', 'deposit_date']
    filter_backends = (filters.SearchFilter,)
    http_method_names = ['get', 'post', 'head', 'put', 'patch']

    def perform_create(self, serializer):
        try:
            book = Book.objects.get(pk=self.request.data['book'])
        except ObjectDoesNotExist:
            raise APIException("Requested Book Does Not Exist.")
        try:
            issue_request = IssueRequest.objects.get(
                book=self.request.data['book'], requester=self.request.data['borrower'])
        except ObjectDoesNotExist:
            issue_request = None
        if book.available > 0 and book.quantity > 0 and\
                check_book_not_issued_to_user(self.request.data['borrower'], self.request.data['book']):
            book.available -= 1
            serializer.save()
            book.save()
            if issue_request and issue_request.request_status == 'RQ':
                issue_request.request_status = IssueRequest.RequestStatus.Issued
                issue_request.save()
        else:
            raise APIException("There was a problem while Issuing this book. \n "
                               "Possible Reasons : "
                               "1. Either Book is not available. "
                               "2. Book is already issued to user.")


class IssueLogExportAsCSV(views.APIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = BookIssueLogSerializer

    def get_serializer(self, queryset, many=True):
        return self.serializer_class(queryset, many=many)

    def get(self, request):
        start = self.request.query_params.get('start_date', date.today())
        end = self.request.query_params.get('end_date', date.today())
        type_of_data = self.request.query_params.get('type', 'issued')

        if type_of_data == 'issued':
            issue_log_qs = IssueLog.objects.filter(issued_date__range=[start, end])
        elif type_of_data == 'deposited':
            issue_log_qs = IssueLog.objects.filter(deposit_date__range=[start, end])
        elif type_of_data == 'delayed':
            issue_log_qs = IssueLog.objects.filter(due_date__range=[start, end], penalty__gt=0)
        else:
            issue_log_qs = IssueLog.objects.filter(issued_date__range=[start, end])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        serializer = self.get_serializer(
            issue_log_qs,
            many=True
        )
        header = BookIssueLogSerializer.Meta.fields
        writer = csv.DictWriter(response, fieldnames=header)
        writer.writeheader()
        for row in serializer.data:
            writer.writerow(row)

        return response
