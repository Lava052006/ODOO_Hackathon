from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from datetime import date, timedelta, datetime
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer
from apps.accounts.models import User

@api_view(['GET'])
@permission_classes([AllowAny])
def attendance_summary_view(request):
    week_offset = int(request.GET.get('weekOffset', 0))
    # Context anchor: Friday 22 Aug 2026
    anchor_today = date(2026, 8, 22)
    view_today = anchor_today + timedelta(weeks=week_offset)
    total_employees = max(User.objects.filter(role='employee').count(), 1)
    
    # Query records for view date (or anchor if viewing historical)
    query_date = min(view_today, anchor_today)
    records = AttendanceRecord.objects.filter(date=query_date).select_related('employee')

    # 1. Summary Metrics
    present_count = records.filter(status='Present').count()
    remote_count = records.filter(status='Remote').count()
    exceptions_qs = records.filter(is_exception=True).select_related('employee')
    exceptions_count = exceptions_qs.count()

    # Average check-in calculation
    valid_times = []
    for r in records:
        if r.check_in and r.check_in != '—' and ':' in r.check_in:
            try:
                h, m = map(int, r.check_in.split(':'))
                valid_times.append(h * 60 + m)
            except ValueError:
                pass
    
    if valid_times:
        avg_minutes = sum(valid_times) // len(valid_times)
        avg_check_in_str = f"{avg_minutes // 60:02d}:{avg_minutes % 60:02d}"
    else:
        avg_check_in_str = "09:06"

    # 2. Weekly Attendance Chart
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    days_chart = []
    base_monday = date(2026, 8, 18) + timedelta(weeks=week_offset)
    for d_idx, d_name in enumerate(day_names):
        cur_date = base_monday + timedelta(days=d_idx)
        is_future = cur_date > anchor_today

        if is_future:
            days_chart.append({
                "day": d_name,
                "date": cur_date.day,
                "value": 0,
                "tone": "future",
                "isFuture": True,
                "label": "Upcoming"
            })
            continue

        p_count = AttendanceRecord.objects.filter(
            date=cur_date, status__in=['Present', 'Remote', 'Late', 'Half-day']
        ).count()
        val = round((p_count / total_employees) * 100) if total_employees else 0
        tone = "good" if val >= 90 else "warn" if val >= 80 else "low"
        days_chart.append({
            "day": d_name,
            "date": cur_date.day,
            "value": val,
            "tone": tone,
            "isFuture": False,
            "label": f"{val}%"
        })

    # 3. Exceptions
    exceptions_list = []
    for e in exceptions_qs[:15]:
        name = e.employee.get_full_name() or e.employee.username
        initials = "".join([p[0] for p in name.split() if p])
        exceptions_list.append({
            'id': e.id,
            'employeeId': e.employee.employee_id,
            'name': name,
            'initials': initials,
            'issue': e.issue or f"Missing check-in · {e.date.strftime('%d %b')}",
            'time': e.exception_time or "2h",
            'color': e.employee.avatar_color,
            'status': e.status,
            'date': e.date.strftime('%Y-%m-%d'),
        })

    # 4. Live Rows for team attendance table
    serialized_rows = []
    for r in records:
        name = r.employee.get_full_name() or r.employee.username
        initials = "".join([p[0] for p in name.split() if p])
        serialized_rows.append({
            'id': r.id,
            'employeeId': r.employee.employee_id,
            'name': name,
            'initials': initials,
            'status': r.status,
            'tone': r.tone or ('protected' if r.status == 'Present' else 'risk' if r.status in ['Late', 'Absent'] else 'pending'),
            'in': r.check_in,
            'out': r.check_out,
            'hours': r.work_hours,
            'location': r.location,
            'color': r.employee.avatar_color,
            'isException': r.is_exception,
            'issue': r.issue,
        })

    return Response({
        'stats': {
            'presentToday': present_count,
            'presentPercentage': round((present_count / total_employees) * 100, 1),
            'avgCheckIn': avg_check_in_str,
            'exceptionsCount': exceptions_count,
            'remoteToday': remote_count,
            'remotePercentage': round((remote_count / total_employees) * 100, 1)
        },
        'days': days_chart,
        'exceptions': exceptions_list,
        'rows': serialized_rows,
        'canGoForward': week_offset < 0
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def resolve_exception_view(request, pk):
    record = AttendanceRecord.objects.filter(pk=pk).first()
    if not record:
        return Response({'error': 'Attendance record not found'}, status=status.HTTP_404_NOT_FOUND)
    
    action_type = request.data.get('action', 'regularize') # 'regularize', 'half_day', 'dismiss'
    
    if action_type == 'regularize':
        record.status = 'Present'
        record.is_exception = False
        record.check_in = '09:00'
        record.check_out = '18:00'
        record.work_hours = '9h 00m'
        record.tone = 'protected'
        msg = f"{record.employee.get_full_name()}'s attendance regularized to Present (09:00 - 18:00)"
    elif action_type == 'half_day':
        record.status = 'Half-day'
        record.is_exception = False
        record.work_hours = '4h 30m'
        record.tone = 'pending'
        msg = f"{record.employee.get_full_name()}'s attendance recorded as Half-day"
    else:
        record.is_exception = False
        msg = f"Exception dismissed for {record.employee.get_full_name()}"
    
    record.save()
    return Response({'message': msg, 'record': AttendanceRecordSerializer(record).data})


@api_view(['POST'])
@permission_classes([AllowAny])
def toggle_checkin_view(request):
    user = request.user
    if not user.is_authenticated:
        user = User.objects.filter(role='employee').first()
    
    if not user:
        return Response({'error': 'No employee found'}, status=status.HTTP_400_BAD_REQUEST)
    
    today = date(2026, 8, 22)
    now_time_str = timezone.now().strftime('%H:%M')
    record, created = AttendanceRecord.objects.get_or_create(
        employee=user,
        date=today,
        defaults={
            'status': 'Present',
            'check_in': now_time_str,
            'work_hours': '0h 01m',
            'location': user.location or 'New Delhi',
            'tone': 'protected'
        }
    )

    if not created:
        if record.check_out == '—' or not record.check_out:
            record.check_out = now_time_str
            record.status = 'Present'
            record.save()
            checked_in = False
        else:
            record.check_out = '—'
            record.check_in = now_time_str
            record.save()
            checked_in = True
    else:
        checked_in = True

    return Response({
        'checkedIn': checked_in,
        'checkInTime': record.check_in,
        'checkOutTime': record.check_out,
        'hours': record.work_hours,
        'message': 'Checked in successfully' if checked_in else 'Checked out successfully'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def employee_attendance_week(request):
    user = request.user
    if not user.is_authenticated:
        user = User.objects.filter(role='employee').first()
    
    # Return complete calendar days for August 2026 (or active weeks)
    calendar_days = []
    # 1 Aug 2026 to 24 Aug 2026
    start_date = date(2026, 8, 1)
    end_date = date(2026, 8, 24)
    
    cur_date = start_date
    while cur_date <= end_date:
        att = AttendanceRecord.objects.filter(employee=user, date=cur_date).first()
        is_today = (cur_date == date(2026, 8, 22))
        is_future = (cur_date > date(2026, 8, 22))
        day_of_week = cur_date.strftime('%a')
        
        if is_future:
            status_val = 'Scheduled'
            in_val, out_val, hours_val = '—', '—', '—'
        elif att:
            status_val = att.status
            in_val = att.check_in
            out_val = att.check_out
            hours_val = att.work_hours if att.work_hours != '—' else ('—' if att.status in ['Off', 'On leave', 'Absent'] else '8h 30m')
        elif day_of_week in ['Sat', 'Sun']:
            status_val = 'Off'
            in_val, out_val, hours_val = '—', '—', '—'
        else:
            status_val = 'Present'
            in_val, out_val, hours_val = '09:00', '18:00', '9h 00m'

        calendar_days.append({
            "date": cur_date.strftime('%Y-%m-%d'),
            "dayNum": cur_date.day,
            "dayName": day_of_week,
            "status": status_val,
            "in": in_val,
            "out": out_val,
            "hours": hours_val,
            "today": is_today,
            "isFuture": is_future,
            "location": getattr(user, 'location', 'New Delhi') or 'New Delhi'
        })
        cur_date += timedelta(days=1)
        
    # Week slice (18 to 24 Aug)
    current_week = [d for d in calendar_days if 18 <= d['dayNum'] <= 24]

    return Response({
        'week': current_week,
        'calendar': calendar_days,
        'stats': {
            'totalPresent': sum(1 for d in calendar_days if d['status'] == 'Present'),
            'totalHalfDay': sum(1 for d in calendar_days if d['status'] == 'Half-day'),
            'totalRemote': sum(1 for d in calendar_days if d['status'] == 'Remote'),
            'totalOff': sum(1 for d in calendar_days if d['status'] == 'Off'),
            'totalHours': "148h 20m"
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def export_attendance_csv(request):
    today = date(2026, 8, 22)
    records = AttendanceRecord.objects.filter(date=today).select_related('employee')
    header = "Employee,Status,Check-in,Check-out,Work hours,Location\n"
    rows = []
    for r in records:
        name = r.employee.get_full_name() or r.employee.username
        rows.append(f"{name},{r.status},{r.check_in},{r.check_out},{r.work_hours},{r.location}")
    
    content = header + "\n".join(rows)
    response = HttpResponse(content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ARIA-attendance-22-Aug-2026.csv"'
    return response
