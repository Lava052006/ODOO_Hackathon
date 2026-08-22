from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from datetime import date
from .models import ShiftAssignment, RosterState
from apps.accounts.models import User
from apps.core.models import Notification, ActivityEvent

BASE_SHIFTS = {
    'M': {'code': 'M', 'label': 'Morning', 'type': 'morning'},
    'E': {'code': 'E', 'label': 'Evening', 'type': 'evening'},
    'N': {'code': 'N', 'label': 'Night', 'type': 'night'},
    'L': {'code': 'L', 'label': 'Leave', 'type': 'leave'},
    'W': {'code': 'W', 'label': 'Weekly off', 'type': 'off'},
}

@api_view(['GET'])
@permission_classes([AllowAny])
def roster_dashboard_view(request):
    state = RosterState.objects.first()
    is_published = state.is_published if state else False

    days = [
        {"name": "Mon", "date": 18},
        {"name": "Tue", "date": 19},
        {"name": "Wed", "date": 20},
        {"name": "Thu", "date": 21},
        {"name": "Fri", "date": 22},
        {"name": "Sat", "date": 23},
        {"name": "Sun", "date": 24}
    ]

    # Map core display employees + sample list
    employees = list(User.objects.filter(role='employee')[:8])
    people = []

    for emp in employees:
        shifts = []
        for day in days:
            target_date = date(2026, 8, day['date'])
            assignment = ShiftAssignment.objects.filter(employee=emp, date=target_date).first()
            if assignment:
                shifts.append({
                    'code': assignment.code,
                    'label': assignment.label,
                    'type': assignment.shift_type
                })
            else:
                shifts.append({**BASE_SHIFTS['M']})
        
        people.append({
            'name': emp.get_full_name() or emp.username,
            'initials': "".join([p[0] for p in (emp.get_full_name() or emp.username).split() if p]),
            'role': emp.department,
            'color': emp.avatar_color,
            'employeeId': emp.employee_id,
            'shifts': shifts
        })

    # Department Coverage Analytics computed dynamically from database
    depts = ['Engineering', 'Customer Success', 'Operations', 'Finance']
    teams = []
    for d in depts:
        dept_users = User.objects.filter(role='employee', department=d)
        user_count = dept_users.count()
        req_count = max(user_count * 5, 10) # 5 workdays per employee
        duty_shifts = ShiftAssignment.objects.filter(
            employee__department=d,
            date__range=[date(2026, 8, 18), date(2026, 8, 24)],
            code__in=['M', 'E', 'N']
        ).count()
        coverage_val = min(100, round((duty_shifts / req_count) * 100)) if req_count else 100
        
        teams.append({
            "name": d,
            "detail": f"{min(duty_shifts // 5, user_count)} / {user_count} required",
            "value": coverage_val
        })

    overall_coverage = round(sum(t['value'] for t in teams) / len(teams)) if teams else 98

    return Response({
        'published': is_published,
        'coveragePercent': 100 if is_published else overall_coverage,
        'days': days,
        'people': people,
        'teams': teams
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def update_shift_view(request):
    employee_id = request.data.get('employeeId')
    day_date = request.data.get('date', 18)
    code = request.data.get('code', 'M')

    user = User.objects.filter(employee_id__iexact=employee_id).first()
    if not user:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    
    target_date = date(2026, 8, int(day_date))
    assignment, _ = ShiftAssignment.objects.get_or_create(employee=user, date=target_date)
    assignment.code = code
    assignment.save()

    return Response({
        'shift': {
            'code': assignment.code,
            'label': assignment.label,
            'type': assignment.shift_type
        },
        'message': f"{user.get_full_name()}'s shift updated"
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def publish_roster_view(request):
    state, _ = RosterState.objects.get_or_create(defaults={'week_start': date(2026, 8, 18)})
    state.is_published = True
    state.coverage_percent = 100
    state.save()

    Notification.objects.create(
        title='Roster published',
        detail='Support team · 18–24 August',
        icon='calendar',
        time_text='Just now',
        is_read=False
    )

    ActivityEvent.objects.create(
        title='Roster coverage finalized',
        detail='Next week published · 100% coverage',
        icon='calendar',
        tone='mint',
        time_text='Just now'
    )

    return Response({'published': True, 'message': 'Roster published and team notified'})
