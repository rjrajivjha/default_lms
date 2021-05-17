from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, IssueRequestViewSet, BookIssueLogViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'issue_logs', BookIssueLogViewSet)
router.register(r'issue_requests', IssueRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]