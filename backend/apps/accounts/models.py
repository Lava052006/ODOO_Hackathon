from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'HR Administrator'),
        ('employee', 'Employee'),
    ]

    DEPARTMENT_CHOICES = [
        ('Engineering', 'Engineering'),
        ('Product', 'Product'),
        ('Customer Success', 'Customer Success'),
        ('Finance', 'Finance'),
        ('Operations', 'Operations'),
        ('People', 'People'),
    ]

    EMPLOYMENT_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
    ]

    employee_id = models.CharField(max_length=20, unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    phone = models.CharField(max_length=30, blank=True, default='+91 98765 43210')
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, default='Connaught Place, New Delhi')
    emergency_contact = models.CharField(max_length=100, blank=True, default='')
    emergency_phone = models.CharField(max_length=30, blank=True, default='')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='Engineering')
    job_title = models.CharField(max_length=100, default='Software Engineer')
    manager = models.CharField(max_length=100, blank=True, default='Arjun Mehta')
    employment_type = models.CharField(max_length=30, choices=EMPLOYMENT_CHOICES, default='Full-time')
    joining_date = models.DateField(default=timezone.now)
    location = models.CharField(max_length=100, default='New Delhi')
    shift = models.CharField(max_length=100, default='General · 09:00-18:00')
    avatar_color = models.CharField(max_length=20, default='teal')
    photo_url = models.TextField(blank=True, default='')
    is_probation = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'employee_id']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.employee_id})"


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='employee_docs/', null=True, blank=True)
    meta = models.CharField(max_length=255, blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.employee_id} - {self.name}"


class OTPVerification(models.Model):
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - {self.code}"
