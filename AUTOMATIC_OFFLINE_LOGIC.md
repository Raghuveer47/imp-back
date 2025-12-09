# Automatic Employee Offline Logic

## 🕐 **Overview**

This feature automatically marks employees as **OFFLINE** based on two time-based rules:

1. **No login for more than 1 hour** → OFFLINE
2. **No location update for more than 30 minutes** → OFFLINE

## 📋 **Rules**

### **Online Status Requirements**
An employee is considered **ONLINE** only if:
- ✅ Has logged in within the last **1 hour** AND
- ✅ Has sent location within the last **30 minutes**

### **Offline Triggers**
An employee is marked **OFFLINE** if:
- ❌ No login activity for **> 1 hour** OR
- ❌ No location update for **> 30 minutes**

## 🔧 **Implementation**

### **Backend Logic**
The logic is implemented in `employees/views.py`:

```python
def check_employee_online_status(employee):
    now = timezone.now()
    
    # Get latest attendance and location
    latest_attendance = Attendance.objects.filter(employee=employee).order_by('-timestamp').first()
    latest_location = EmployeeLocation.objects.filter(employee=employee).order_by('-timestamp').first()
    
    # Check login time (1 hour rule)
    if latest_attendance:
        time_since_login = now - latest_attendance.timestamp
        if time_since_login > timedelta(hours=1):
            return False  # OFFLINE
    
    # Check location time (30 minutes rule)
    if latest_location:
        time_since_location = now - latest_location.timestamp
        if time_since_location > timedelta(minutes=30):
            return False  # OFFLINE
    
    return True  # ONLINE
```

### **API Endpoints**
- **`/api/live-employee-locations/`** - Returns employee locations with automatic offline status
- **`/api/employee-locations/`** - Returns employee locations with automatic offline status
- **`/api/update-employee-status/`** - Manually trigger status update

## 🚀 **Usage**

### **1. Automatic Status Updates**
The system automatically checks employee status when:
- Frontend requests employee locations
- Live location monitoring is active
- Manual status update is triggered

### **2. Manual Status Update**
```bash
# Using Django management command
python manage.py update_employee_status

# Using API endpoint
curl -X POST http://localhost:8000/api/update-employee-status/
```

### **3. Testing the Logic**
```bash
# Create test data
python test_offline_logic.py create

# Test the logic
python test_offline_logic.py
```

## 📊 **Frontend Integration**

### **LiveLocationMap Page**
- Automatically shows offline employees
- Updates status every 10 seconds
- Shows "OFFLINE" badge for inactive employees

### **EmployeeList Page**
- Google Maps shows offline employees
- Status indicators show online/offline state
- Real-time updates reflect automatic offline logic

## ⏰ **Timing Examples**

### **Scenario 1: Employee Logs In But Doesn't Share Location**
```
10:00 AM - Employee logs in ✅
10:30 AM - No location update for 30 minutes ❌
10:30 AM - Status: OFFLINE
```

### **Scenario 2: Employee Shares Location But Doesn't Log In**
```
09:00 AM - Employee logs in ✅
10:00 AM - Employee shares location ✅
11:00 AM - No login for 1 hour ❌
11:00 AM - Status: OFFLINE
```

### **Scenario 3: Active Employee**
```
10:00 AM - Employee logs in ✅
10:15 AM - Employee shares location ✅
10:45 AM - Employee shares location ✅
11:00 AM - Status: ONLINE (both conditions met)
```

## 🔄 **Automation Options**

### **Option 1: Cron Job (Recommended)**
Add to your server's crontab:
```bash
# Update employee status every 5 minutes
*/5 * * * * cd /path/to/your/project && python manage.py update_employee_status
```

### **Option 2: Django Celery Beat**
```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'update-employee-status': {
        'task': 'employees.tasks.update_employee_status',
        'schedule': 300.0,  # Every 5 minutes
    },
}
```

### **Option 3: Frontend Polling**
The frontend already polls for updates every 10 seconds, which will trigger the offline logic automatically.

## 🛠️ **Configuration**

### **Customize Time Limits**
To change the time limits, modify the `check_employee_online_status` function:

```python
# Change to 2 hours for login
if time_since_login > timedelta(hours=2):  # Instead of 1 hour

# Change to 45 minutes for location
if time_since_location > timedelta(minutes=45):  # Instead of 30 minutes
```

### **Add More Conditions**
You can add additional conditions to the offline logic:

```python
# Example: Check if employee is on leave
if employee.is_on_leave:
    return False  # OFFLINE

# Example: Check working hours
current_hour = now.hour
if current_hour < 9 or current_hour > 17:
    return False  # OFFLINE (outside working hours)
```

## 📈 **Monitoring**

### **Logs**
The system logs status changes:
```
🕐 Employee John Doe hasn't logged in for 1.2 hours - marking offline
📍 Employee Jane Smith hasn't sent location for 35.5 minutes - marking offline
✅ Updated John Doe to offline
```

### **API Response**
```json
{
  "employee_id": "EMP001",
  "employee_name": "John Doe",
  "status": "offline",
  "last_updated": "2024-01-15T10:30:00Z",
  "reason": "No login for 1.2 hours"
}
```

## ✅ **Benefits**

1. **Automatic Management** - No manual intervention needed
2. **Real-time Accuracy** - Status reflects actual activity
3. **Configurable Rules** - Easy to adjust time limits
4. **Frontend Integration** - Works seamlessly with existing UI
5. **Performance Optimized** - Efficient database queries
6. **Scalable** - Works with any number of employees

## 🔍 **Troubleshooting**

### **Employee Always Shows Offline**
1. Check if employee has recent attendance records
2. Check if employee has recent location updates
3. Verify timezone settings
4. Check database timestamps

### **Status Not Updating**
1. Ensure management command is running
2. Check API endpoint is accessible
3. Verify frontend is polling correctly
4. Check server logs for errors

### **Custom Time Limits**
1. Modify the `check_employee_online_status` function
2. Restart the application
3. Test with the test script
4. Update documentation 