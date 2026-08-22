from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.utils import timezone
from datetime import date
from .models import User, Document, OTPVerification
from .serializers import UserSerializer, SigninSerializer, SignupSerializer, VerifyOTPSerializer, DocumentSerializer
from apps.payroll.models import SalaryStructure
from apps.attendance.models import AttendanceRecord

@api_view(['POST'])
@permission_classes([AllowAny])
def signin_view(request):
    serializer = SigninSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email'].lower()
    password = serializer.validated_data['password']
    
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        user = User.objects.filter(username__iexact=email).first()
    
    if user and user.check_password(password):
        login(request, user)
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Sign in successful'
        })
    
    return Response({'error': 'Incorrect email or password. Try a demo account or create a new one.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email'].lower()
    employee_id = serializer.validated_data['employeeId'].upper()
    
    if User.objects.filter(email__iexact=email).exists():
        return Response({'error': 'An account with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(employee_id__iexact=employee_id).exists():
        return Response({'error': 'An account with this Employee ID already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    
    OTPVerification.objects.filter(email=email).delete()
    OTPVerification.objects.create(email=email, code='247109')
    
    return Response({'message': 'Verification code sent to email', 'demoCode': '247109'})


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_view(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email'].lower()
    code = serializer.validated_data['code']
    
    otp = OTPVerification.objects.filter(email=email, code=code).first()
    if not otp and code != '247109':
        return Response({'error': 'That code is incorrect. Use 247109 for this demo.'}, status=status.HTTP_400_BAD_REQUEST)
    
    first_name = request.data.get('firstName', '')
    last_name = request.data.get('lastName', '')
    employee_id = request.data.get('employeeId', '').upper()
    role = request.data.get('role', 'employee')
    password = request.data.get('password', 'Aria@2026')
    
    user, created = User.objects.get_or_create(
        username=email,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'employee_id': employee_id or f"EMP{User.objects.count() + 1000}",
            'role': role,
            'department': 'Engineering' if role == 'employee' else 'People',
            'job_title': 'Software Engineer' if role == 'employee' else 'HR Administrator',
            'avatar_color': 'teal'
        }
    )
    if created:
        user.set_password(password)
        user.save()
        SalaryStructure.objects.get_or_create(employee=user)
    
    login(request, user)
    userData = UserSerializer(user).data
    userData['newlyVerified'] = True
    return Response({'user': userData, 'message': 'Account verified and ready'})


@api_view(['GET'])
def me_view(request):
    if request.user.is_authenticated:
        return Response({'user': UserSerializer(request.user).data})
    return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out successfully'})


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    lookup_field = 'employee_id'

    def get_queryset(self):
        from apps.attendance.models import AttendanceRecord
        from django.db.models import Prefetch
        today = date(2026, 8, 22)
        return User.objects.filter(role='employee').prefetch_related(
            'documents',
            Prefetch('attendances', queryset=AttendanceRecord.objects.filter(date=today), to_attr='today_attendance')
        ).order_by('id')

    def create(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name', '').strip()
        parts = name.split(' ', 1) if name else ['', '']
        first_name = data.get('firstName') or parts[0] or 'New'
        last_name = data.get('lastName') or (parts[1] if len(parts) > 1 else '') or 'Employee'
        email = data.get('email', '').strip().lower()
        employee_id = (data.get('employeeId') or f"EMP{User.objects.count() + 1000}").strip().upper()
        department = data.get('department', 'Engineering')
        job_title = data.get('role') or data.get('jobTitle', 'Software Engineer')
        location = data.get('location', 'New Delhi')
        
        if not email:
            email = f"{first_name.lower()}.{last_name.lower()}@aria.com"
        
        if User.objects.filter(email__iexact=email).exists():
            return Response({'error': 'An employee with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(employee_id__iexact=employee_id).exists():
            return Response({'error': 'An employee with this ID already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            employee_id=employee_id,
            role='employee',
            department=department,
            job_title=job_title,
            location=location,
            avatar_color='teal',
            joining_date=date(2026, 8, 22),
            is_probation=True
        )
        user.set_password('Aria@2026')
        user.save()
        
        # Default salary & attendance
        SalaryStructure.objects.create(employee=user, basic=50000, hra=15000, special=10000, other=3000, deductions=9000)
        AttendanceRecord.objects.create(
            employee=user,
            date=date(2026, 8, 22),
            status='Present',
            tone='protected',
            check_in='09:00',
            work_hours='0h 01m',
            location=location
        )
        
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        today = date(2026, 8, 22)
        total_active = User.objects.filter(role='employee', is_active=True).count()
        depts_count = User.objects.filter(role='employee').values('department').distinct().count()
        new_joiners = User.objects.filter(
            role='employee', joining_date__year=today.year, joining_date__month=today.month
        ).count()
        on_probation = User.objects.filter(role='employee', is_probation=True).count()

        return Response({
            'activeEmployees': total_active,
            'departmentCount': depts_count,
            'newJoiners': new_joiners,
            'onProbation': on_probation,
        })

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        user = User.objects.filter(employee_id__iexact=lookup_value).first()
        if not user:
            user = User.objects.filter(id=lookup_value).first() if lookup_value.isdigit() else None
        if not user:
            from rest_framework.exceptions import NotFound
            raise NotFound('Employee not found')
        return user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        
        data = request.data
        if 'name' in data and data['name']:
            parts = data['name'].split(' ', 1)
            instance.first_name = parts[0]
            instance.last_name = parts[1] if len(parts) > 1 else ''
        if 'email' in data:
            instance.email = data['email']
        if 'phone' in data:
            instance.phone = data['phone']
        if 'birthDate' in data:
            instance.birth_date = data['birthDate'] or None
        if 'address' in data:
            instance.address = data['address']
        if 'emergencyContact' in data:
            instance.emergency_contact = data['emergencyContact']
        if 'emergencyPhone' in data:
            instance.emergency_phone = data['emergencyPhone']
        if 'department' in data:
            instance.department = data['department']
        if 'role' in data:
            instance.job_title = data['role']
        if 'jobTitle' in data:
            instance.job_title = data['jobTitle']
        if 'manager' in data:
            instance.manager = data['manager']
        if 'employmentType' in data:
            instance.employment_type = data['employmentType']
        if 'joiningDate' in data and data['joiningDate']:
            instance.joining_date = data['joiningDate']
        if 'location' in data:
            instance.location = data['location']
        if 'shift' in data:
            instance.shift = data['shift']
        if 'photoUrl' in data:
            instance.photo_url = data['photoUrl']
        
        instance.save()
        return Response(UserSerializer(instance).data)

    @action(detail=True, methods=['post'])
    def documents(self, request, employee_id=None):
        employee = self.get_object()
        name = request.data.get('name', 'Document')
        meta = request.data.get('meta', f"Uploaded just now · {timezone.now().strftime('%d %b %Y')}")
        file_obj = request.FILES.get('file', None)
        
        doc = Document.objects.create(
            user=employee,
            name=name,
            file=file_obj,
            meta=meta
        )
        return Response(DocumentSerializer(doc).data, status=status.HTTP_201_CREATED)
