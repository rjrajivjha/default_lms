from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .utils import get_due_date


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('User must have a valid email')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email'), max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(_('staff status'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.name if self.name else self.email


class Book(models.Model):
    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')

    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    author = models.CharField(max_length=255, blank=False, null=False)
    quantity = models.IntegerField()
    available = models.IntegerField()

    objects = models.Manager()

    def __str__(self):
        return self.title


class IssueRequest(models.Model):

    class Meta:
        verbose_name = _('Issue Request')
        verbose_name_plural = _('Issue Requests')

    class RequestStatus(models.TextChoices):
        Requested = 'RQ', _('Requested')
        Issued = 'IS', _('Issued')
        Denied = 'DN', _('Denied')

    requester = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=False)
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING, blank=False)
    request_status = models.CharField(max_length=2, choices=RequestStatus.choices, default=RequestStatus.Requested)
    request_date = models.DateField(auto_now_add=True)

    objects = models.Manager()


class IssueLog(models.Model):
    borrower = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=False)
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING, blank=False)
    issued_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(default=get_due_date)
    deposit_date = models.DateField(null=True, blank=True)
    penalty = models.IntegerField(default=0)

    objects = models.Manager()

    def __str__(self):
        return f'{self.borrower} has book titled : {self.book} issued on {self.issued_date} due on {self.due_date}'


