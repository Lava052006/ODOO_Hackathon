from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from django.db import transaction
from apps.accounts.models import User, Document
from apps.attendance.models import AttendanceRecord
from apps.leaves.models import LeaveRequest
from apps.payroll.models import SalaryStructure, PayrollRun
from apps.roster.models import ShiftAssignment, RosterState
from apps.core.models import Notification, NotificationPreference, ActivityEvent

class Command(BaseCommand):
    help = 'Seeds PostgreSQL database with 120 realistic employees and full dynamic dataset'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding 120 employees and dynamic dataset in PostgreSQL...')

        # Clear existing non-admin data if needed or ensure clean state
        # Keep admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin@aria.com',
            defaults={
                'email': 'admin@aria.com',
                'first_name': 'Arjun',
                'last_name': 'Mehta',
                'employee_id': 'EMP1001',
                'role': 'admin',
                'phone': '+91 98111 00001',
                'department': 'People',
                'job_title': 'HR Administrator',
                'location': 'New Delhi',
                'avatar_color': 'amber',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('Aria@2026')
        admin_user.save()

        # Key demo employees
        core_employees_data = [
            {'email': 'employee@aria.com', 'first_name': 'Neha', 'last_name': 'Sharma', 'employee_id': 'EMP1024', 'role': 'employee', 'department': 'Engineering', 'job_title': 'Software Engineer', 'location': 'New Delhi', 'avatar_color': 'teal', 'probation': False, 'salary': 95000},
            {'email': 'aisha@aria.com', 'first_name': 'Aisha', 'last_name': 'Khan', 'employee_id': 'EMP1038', 'role': 'employee', 'department': 'Product', 'job_title': 'UX Designer', 'location': 'Mumbai', 'avatar_color': 'blue', 'probation': False, 'salary': 86800},
            {'email': 'rohit@aria.com', 'first_name': 'Rohit', 'last_name': 'Sharma', 'employee_id': 'EMP0991', 'role': 'employee', 'department': 'Customer Success', 'job_title': 'Support Specialist', 'location': 'Pune', 'avatar_color': 'coral', 'probation': False, 'salary': 73400},
            {'email': 'priya@aria.com', 'first_name': 'Priya', 'last_name': 'Desai', 'employee_id': 'EMP1018', 'role': 'employee', 'department': 'Finance', 'job_title': 'Finance Analyst', 'location': 'Bengaluru', 'avatar_color': 'violet', 'probation': False, 'salary': 98600},
            {'email': 'vikram@aria.com', 'first_name': 'Vikram', 'last_name': 'Singh', 'employee_id': 'EMP1042', 'role': 'employee', 'department': 'Operations', 'job_title': 'Operations Lead', 'location': 'New Delhi', 'avatar_color': 'amber', 'probation': False, 'salary': 91000},
            {'email': 'meera@aria.com', 'first_name': 'Meera', 'last_name': 'Iyer', 'employee_id': 'EMP0974', 'role': 'employee', 'department': 'People', 'job_title': 'People Partner', 'location': 'Chennai', 'avatar_color': 'teal', 'probation': False, 'salary': 88000},
        ]

        first_names = [
            "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Muhammad", "Sai", "Ayaan", "Krishna",
            "Ishaan", "Shaurya", "Atharva", "Advik", "Pranav", "Advaith", "Aaryan", "Dhruv", "Kabir", "Rishi",
            "Ananya", "Diya", "Gauri", "Isha", "Kavya", "Khushi", "Kiara", "Myra", "Navya", "Pari",
            "Prisha", "Riya", "Saanvi", "Sara", "Shreya", "Siya", "Tanvi", "Vanya", "Zara", "Tara"
        ]
        last_names = [
            "Patel", "Shah", "Reddy", "Nair", "Kapoor", "Chopra", "Verma", "Bhat", "Rao", "Joshi",
            "Menon", "Kulkarni", "Deshmukh", "Choudhury", "Bose", "Ghosh", "Banerjee", "Sengupta", "Pillai", "Gupta"
        ]
        departments = [
            ('Engineering', 'Software Engineer'),
            ('Engineering', 'Frontend Developer'),
            ('Engineering', 'Backend Engineer'),
            ('Engineering', 'QA Engineer'),
            ('Product', 'Product Manager'),
            ('Product', 'UI/UX Designer'),
            ('Customer Success', 'Support Specialist'),
            ('Customer Success', 'Account Manager'),
            ('Finance', 'Financial Analyst'),
            ('Finance', 'Accountant'),
            ('Operations', 'Operations Executive'),
            ('Operations', 'Logistics Coordinator'),
            ('People', 'HR Specialist'),
            ('People', 'Talent Partner'),
        ]
        locations = ["New Delhi", "Bengaluru", "Mumbai", "Pune", "Chennai", "Hyderabad"]
        colors = ["teal", "blue", "coral", "violet", "amber"]

        # Cache hashed password for fast seeding
        from django.contrib.auth.hashers import make_password
        hashed_password = make_password('Aria@2026')

        all_employees = []
        # Create core employees
        for c in core_employees_data:
            emp, _ = User.objects.get_or_create(
                username=c['email'],
                defaults={
                    'email': c['email'],
                    'first_name': c['first_name'],
                    'last_name': c['last_name'],
                    'employee_id': c['employee_id'],
                    'role': 'employee',
                    'department': c['department'],
                    'job_title': c['job_title'],
                    'location': c['location'],
                    'avatar_color': c['avatar_color'],
                    'joining_date': date(2024, 4, 15),
                    'is_probation': c['probation'],
                    'password': hashed_password,
                }
            )
            if emp.password != hashed_password:
                emp.password = hashed_password
                emp.save()
            all_employees.append(emp)

            # Documents for Neha
            if emp.employee_id == 'EMP1024' and not Document.objects.filter(user=emp).exists():
                Document.objects.create(user=emp, name='Aadhaar Card.pdf', meta='Identity · Uploaded 10 Aug 2026')
                Document.objects.create(user=emp, name='PAN Card.pdf', meta='Tax document · Uploaded 10 Aug 2026')
                Document.objects.create(user=emp, name='Employment Contract.pdf', meta='Employment · Uploaded 15 Apr 2024')

        # Generate additional employees to reach exactly 120 employees
        current_emp_count = User.objects.filter(role='employee').count()
        needed = 120 - current_emp_count
        
        # 5 new joiners in August 2026, 7 on probation
        random.seed(42) # Deterministic
        for idx in range(needed):
            emp_num = 1050 + idx
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            email = f"{fn.lower()}.{ln.lower()}{idx+1}@aria.com"
            dept, title = random.choice(departments)
            loc = random.choice(locations)
            color = random.choice(colors)
            
            # August joiner? (First 5)
            if idx < 5:
                join_date = date(2026, 8, 1 + (idx * 3))
                probation = True
            elif idx < 7: # 7 on probation total
                join_date = date(2026, 6, 15)
                probation = True
            else:
                join_date = date(2023 + (idx % 3), 1 + (idx % 12), 1 + (idx % 25))
                probation = False

            emp, _ = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': fn,
                    'last_name': ln,
                    'employee_id': f"EMP{emp_num}",
                    'role': 'employee',
                    'department': dept,
                    'job_title': title,
                    'location': loc,
                    'avatar_color': color,
                    'joining_date': join_date,
                    'is_probation': probation,
                    'password': hashed_password,
                }
            )
            if emp.password != hashed_password:
                emp.password = hashed_password
                emp.save()
            all_employees.append(emp)

        total_emp_list = list(User.objects.filter(role='employee'))
        self.stdout.write(f"Total employees in database: {len(total_emp_list)}")

        # 2. Salary Structures (Total Gross around ₹84.6L)
        # Average salary around ₹70,500 * 120 = ₹84,60,000 (84.6L)
        for emp in total_emp_list:
            if emp.employee_id == 'EMP1024':
                b, h, s, o, d = 60000, 18000, 12000, 5000, 12680
            elif emp.employee_id == 'EMP1038':
                b, h, s, o, d = 56000, 16800, 10000, 4000, 10840
            elif emp.employee_id == 'EMP0991':
                b, h, s, o, d = 48000, 14400, 8000, 3000, 9240
            elif emp.employee_id == 'EMP1018':
                b, h, s, o, d = 62000, 18600, 13000, 5000, 13450
            else:
                base_sal = 45000 + (hash(emp.employee_id) % 30000)
                b = int(base_sal * 0.55)
                h = int(base_sal * 0.20)
                s = int(base_sal * 0.15)
                o = int(base_sal * 0.10)
                d = int(base_sal * 0.12)
            
            SalaryStructure.objects.update_or_create(
                employee=emp,
                defaults={'basic': b, 'hra': h, 'special': s, 'other': o, 'deductions': d}
            )

        PayrollRun.objects.update_or_create(
            month='August',
            year=2026,
            defaults={
                'is_closed': False,
                'gross_amount_lakhs': 84.6,
                'readiness_percent': 90,
                'exceptions_count': 12,
                'pay_date': '31 Aug 2026'
            }
        )

        # 3. Seed Today's Attendance (Today = 22 Aug 2026)
        # Breakdown: 98 Present, 10 Remote, 4 On leave, 4 Absent, 2 Half-day, 2 Late = 120
        today = date(2026, 8, 22)
        
        # Specific core assignments
        status_allocations = (
            [('Present', False, '09:04', '—', '6h 42m')] * 88 +
            [('Remote', False, '09:00', '—', '6h 45m')] * 10 +
            [('On leave', False, '—', '—', '—')] * 4 +
            [('Absent', False, '—', '—', '—')] * 4 +
            [('Half-day', False, '09:15', '13:30', '4h 15m')] * 2 +
            [('Late', True, '09:42', '—', '6h 04m')] * 6 + # exceptions
            [('Present', True, '—', '—', '—')] * 6 # missing checkin exceptions
        )
        
        for idx, emp in enumerate(total_emp_list):
            if idx < len(status_allocations):
                st, is_ex, cin, cout, hrs = status_allocations[idx]
            else:
                st, is_ex, cin, cout, hrs = 'Present', False, '09:05', '—', '6h 40m'
            
            # Special core mappings
            if emp.employee_id == 'EMP1024': # Neha
                st, is_ex, cin, cout, hrs = 'Present', False, '09:04', '—', '6h 42m'
            elif emp.employee_id == 'EMP1018': # Priya
                st, is_ex, cin, cout, hrs = 'Present', False, '08:58', '—', '6h 48m'
            elif emp.employee_id == 'EMP1038': # Aisha
                st, is_ex, cin, cout, hrs = 'On leave', False, '—', '—', '—'
            elif emp.employee_id == 'EMP1042': # Vikram
                st, is_ex, cin, cout, hrs = 'Late', True, '09:42', '—', '6h 04m'
            elif emp.employee_id == 'EMP0991': # Rohit
                st, is_ex, cin, cout, hrs = 'Present', True, '—', '—', '—'

            tone = 'protected' if st == 'Present' else 'risk' if (is_ex or st == 'Late' or st == 'Absent') else 'pending' if st == 'On leave' else 'good'
            issue = 'Late arrival · 42 minutes' if st == 'Late' else 'Missing check-in · 21 Aug' if (is_ex and cin == '—') else ''
            
            AttendanceRecord.objects.update_or_create(
                employee=emp,
                date=today,
                defaults={
                    'status': st,
                    'tone': tone,
                    'check_in': cin,
                    'check_out': cout,
                    'work_hours': hrs,
                    'location': emp.location,
                    'is_exception': is_ex,
                    'issue': issue,
                    'exception_time': '2h' if is_ex else '',
                }
            )

        # 4. Past 6 days attendance history for 7-day signals
        day_percents = [94, 97, 91, 96, 98, 74, 42]
        for past_idx in range(1, 7):
            past_date = today - timedelta(days=past_idx)
            rate = day_percents[past_idx % 7]
            present_target = int(120 * (rate / 100))
            for idx, emp in enumerate(total_emp_list):
                st = 'Present' if idx < present_target else ('Off' if past_idx >= 5 else 'Absent')
                AttendanceRecord.objects.update_or_create(
                    employee=emp,
                    date=past_date,
                    defaults={
                        'status': st,
                        'tone': 'protected' if st == 'Present' else 'low',
                        'check_in': '09:00' if st == 'Present' else '—',
                        'check_out': '18:00' if st == 'Present' else '—',
                        'work_hours': '9h 00m' if st == 'Present' else '—',
                        'location': emp.location,
                        'is_exception': False,
                    }
                )

        # 5. Leaves (7 pending, 3 approved, 1 rejected)
        LeaveRequest.objects.all().delete()
        core_leaves = [
            {'emp_id': 'EMP1038', 'type': 'Paid leave', 'f': today + timedelta(days=2), 't': today + timedelta(days=3), 'r': 'Paid leave · 24–25 Aug', 'st': 'pending'},
            {'emp_id': 'EMP0991', 'type': 'Work from home', 'f': today - timedelta(days=1), 't': today - timedelta(days=1), 'r': 'Check-in missing · 21 Aug', 'st': 'pending'},
            {'emp_id': 'EMP1018', 'type': 'Sick leave', 'f': today, 't': today, 'r': 'Sick leave · 22 Aug', 'st': 'pending'},
        ]
        for cl in core_leaves:
            u = User.objects.filter(employee_id=cl['emp_id']).first()
            if u:
                LeaveRequest.objects.create(
                    employee=u,
                    leave_type=cl['type'],
                    from_date=cl['f'],
                    to_date=cl['t'],
                    reason=cl['r'],
                    status=cl['st'],
                    team_coverage='92%'
                )

        # 4 more pending leaves to make 7 pending
        for i in range(4):
            emp = total_emp_list[10 + i]
            LeaveRequest.objects.create(
                employee=emp,
                leave_type='Paid leave',
                from_date=today + timedelta(days=3 + i),
                to_date=today + timedelta(days=4 + i),
                reason='Annual family vacation',
                status='pending',
                team_coverage='94%'
            )

        # 3 approved leaves
        for i in range(3):
            emp = total_emp_list[20 + i]
            LeaveRequest.objects.create(
                employee=emp,
                leave_type='Paid leave',
                from_date=today - timedelta(days=1),
                to_date=today + timedelta(days=1),
                reason='Medical checkup',
                status='approved',
                team_coverage='95%'
            )

        # 1 rejected leave
        emp = total_emp_list[30]
        LeaveRequest.objects.create(
            employee=emp,
            leave_type='Unpaid leave',
            from_date=today + timedelta(days=5),
            to_date=today + timedelta(days=8),
            reason='Personal extended leave',
            status='rejected',
            admin_comment='Critical sprint release week',
            team_coverage='80%'
        )

        # 6. Roster Shifts for Week of 18-24 Aug
        RosterState.objects.update_or_create(
            defaults={'week_start': date(2026, 8, 18), 'is_published': False, 'coverage_percent': 98}
        )
        patterns = ["MMEMMWW", "EEMMENW", "MLLMEWW", "NNEMMWW", "MMELEMW", "MMMMMWW"]
        for idx, emp in enumerate(total_emp_list):
            pat = patterns[idx % len(patterns)]
            for d_idx in range(7):
                s_date = date(2026, 8, 18 + d_idx)
                c = pat[d_idx % len(pat)]
                ShiftAssignment.objects.update_or_create(
                    employee=emp,
                    date=s_date,
                    defaults={'code': c}
                )

        # 7. Activity & Notifications
        Notification.objects.all().delete()
        Notification.objects.create(title='Leave request needs review', detail='Aisha Khan · 24–25 Aug', time_text='2 minutes ago', icon='leave', tone='warning', is_read=False)
        Notification.objects.create(title='Payroll check completed', detail='12 employee records need attention', time_text='18 minutes ago', icon='rupee', tone='', is_read=False)
        Notification.objects.create(title='Roster published', detail='Support team · 18–24 August', time_text='1 hour ago', icon='calendar', tone='', is_read=False)
        Notification.objects.create(title='Profile updated', detail='Neha Sharma changed her phone number', time_text='Yesterday', icon='user', tone='', is_read=True)

        ActivityEvent.objects.all().delete()
        ActivityEvent.objects.create(title='Payroll draft is ready', detail='August payroll · 120 employees', time_text='2m', icon='rupee', tone='mint')
        ActivityEvent.objects.create(title='Neha checked in', detail='Connaught Place Office', time_text='8m', icon='check', tone='blue')
        ActivityEvent.objects.create(title='Roster coverage improved', detail='Support team · +6%', time_text='24m', icon='calendar', tone='amber')

        self.stdout.write(self.style.SUCCESS('Successfully populated 120 employees with pure dynamic PostgreSQL data!'))
