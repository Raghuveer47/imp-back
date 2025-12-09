from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView
from django.core.files.base import ContentFile
from sklearn.metrics.pairwise import cosine_similarity
from django.utils.timezone import now
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import Employee, Attendance, OfficeLocation, LocationAlert, EmployeeLocation
from .serializers import EmployeeSerializer, AttendanceSerializer, OfficeLocationSerializer, LocationAlertSerializer
from .utils import get_face_encoding_from_base64, is_within_location, compare_face_descriptors
from .cloudinary_utils import (
    configure_cloudinary, 
    upload_base64_to_cloudinary, 
    prepare_image_for_face_detection
)

import numpy as np
import base64
import io
from PIL import Image
from django.utils import timezone

# Configure Cloudinary
configure_cloudinary()

@api_view(['POST'])
def analyze_face(request):
    try:
        base64_img = request.data.get('image_base64', '')

        if not base64_img:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Remove the prefix if included
        if "," in base64_img:
            base64_img = base64_img.split(",")[1]

        # Decode image to numpy array
        image_data = base64.b64decode(base64_img)
        image = Image.open(io.BytesIO(image_data))
        img_array = np.array(image)

        # For now, return a dummy descriptor since we're not doing face detection on backend
        # The frontend will handle face detection and send descriptors
        dummy_descriptor = np.random.rand(128).astype(np.float32)

        return Response({"descriptor": dummy_descriptor.tolist()}, status=status.HTTP_200_OK)

    except Exception as e:
        print("❌ Analyze Face Error:", e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterEmployeeView(APIView):
    def post(self, request):
        try:
            name = request.data['name']
            employee_id = request.data['employee_id']
            face_image_base64 = request.data['face_image']
            descriptor_list = request.data['descriptor']  # <-- descriptor from frontend
            office_id = request.data['office_id']

            # Validation
            if not descriptor_list or len(descriptor_list) != 128:
                return Response({'error': 'Invalid or missing face descriptor'}, status=400)

            # 🖼️ Upload to Cloudinary
            try:
                cloudinary_url, cloudinary_id = upload_base64_to_cloudinary(
                    face_image_base64, 
                    folder="employee_faces", 
                    public_id=f"employee_{employee_id}"
                )
                print(f"✅ Image uploaded to Cloudinary: {cloudinary_url}")
            except Exception as e:
                print(f"❌ Cloudinary upload failed: {e}")
                # Fallback to local storage
                cloudinary_url = None
                cloudinary_id = None

            # Decode and save face image (local backup)
            if "," in face_image_base64:
                face_image_base64 = face_image_base64.split(",")[1]
            image_data = base64.b64decode(face_image_base64)
            image_file = ContentFile(image_data, name=f"{employee_id}.jpg")

            # Convert descriptor to float32 and store
            descriptor_array = np.array(descriptor_list, dtype=np.float32)

            # Get OfficeLocation instance
            try:
                office_instance = OfficeLocation.objects.get(id=office_id)
            except OfficeLocation.DoesNotExist:
                return Response({'error': 'Invalid office ID'}, status=400)

            # Save employee with Cloudinary URLs
            Employee.objects.create(
                name=name,
                employee_id=employee_id,
                face_image=image_file,  # Local backup
                face_image_cloudinary_url=cloudinary_url,
                face_image_cloudinary_id=cloudinary_id,
                office=office_instance,
                face_encoding=descriptor_array.tobytes()  # now 128-D float32
            )

            return Response({
                'message': 'Employee registered successfully!',
                'cloudinary_url': cloudinary_url,
                'face_detection_status': 'working'
            }, status=201)

        except Exception as e:
            print("❌ Register Error:", e)
            return Response({'error': str(e)}, status=500)

class GetEmployeeByID(RetrieveAPIView):
    lookup_field = 'employee_id'
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
class AttendanceView(APIView):
    def post(self, request):
        try:
            employee_id = request.data['employee_id']
            face_image_base64 = request.data['face_image']
            descriptor_list = request.data.get('descriptor')
            latitude = float(request.data['latitude'])
            longitude = float(request.data['longitude'])
            action = request.data['action']

            if not descriptor_list:
                return Response({'error': 'Missing face descriptor'}, status=400)

            incoming_encoding = np.array(descriptor_list, dtype=np.float32)

            try:
                employee = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=404)

            stored_encoding = np.frombuffer(employee.face_encoding, dtype=np.float32)

            # ✅ Face recognition check
            similarity = cosine_similarity(incoming_encoding.reshape(1, -1), stored_encoding.reshape(1, -1))[0][0]
            print(f"🧠 Cosine Similarity: {similarity:.4f}")

            # Additional validation checks
            if len(incoming_encoding) != 128:
                print(f"❌ Invalid descriptor length: {len(incoming_encoding)}")
                return Response({
                    'error': 'Invalid face descriptor length. Expected 128 dimensions.',
                    'received_length': len(incoming_encoding)
                }, status=400)

            # Check if descriptor is all zeros or empty
            if np.all(incoming_encoding == 0) or np.sum(np.abs(incoming_encoding)) < 1e-6:
                print(f"❌ Empty or zero descriptor detected")
                return Response({
                    'error': 'No face detected in the image. Please ensure your face is clearly visible.',
                    'status': 'no_face_detected'
                }, status=400)

            # Check for NaN or infinite values
            if np.isnan(similarity) or np.isinf(similarity):
                print(f"❌ Invalid similarity value: {similarity}")
                return Response({
                    'error': 'Invalid face descriptor detected. Please try again.',
                    'similarity': 'NaN/Inf'
                }, status=400)

            # Make threshold even stricter - 0.95 for better security
            threshold = 0.95
            if similarity < threshold:
                print(f"❌ Face rejected! Similarity: {similarity:.4f} < {threshold}")
                return Response({
                    'error': f'Face does not match. Similarity: {similarity:.4f} (required: {threshold})',
                    'similarity': round(similarity, 4),
                    'threshold': threshold,
                    'status': 'face_mismatch'
                }, status=403)
            
            print(f"✅ Face accepted! Similarity: {similarity:.4f} >= {threshold}")

            # ✅ Location check
            office = employee.office
            distance = is_within_location(latitude, longitude, office.latitude, office.longitude)
            print(f"📍 Distance from office: {int(distance)} meters")

            if distance > office.radius_meters:
                return Response({
                    'error': f'❌ Location mismatch. You are {int(distance)} meters away from office.',
                    'distance': int(distance),
                    'allowed_radius': office.radius_meters
                }, status=403)

            # 🖼️ Upload to Cloudinary
            try:
                cloudinary_url, cloudinary_id = upload_base64_to_cloudinary(
                    face_image_base64, 
                    folder="attendance_photos", 
                    public_id=f"attendance_{employee_id}_{action}_{int(timezone.now().timestamp())}"
                )
                print(f"✅ Attendance image uploaded to Cloudinary: {cloudinary_url}")
            except Exception as e:
                print(f"❌ Cloudinary upload failed: {e}")
                # Fallback to local storage
                cloudinary_url = None
                cloudinary_id = None

            # ✅ Save image (local backup)
            if "," in face_image_base64:
                face_image_base64 = face_image_base64.split(",")[1]
            image_data = base64.b64decode(face_image_base64)
            image_file = ContentFile(image_data, name=f"{employee_id}_{action}.jpg")

            # ✅ Save attendance with Cloudinary URLs
            Attendance.objects.create(
                employee=employee,
                image=image_file,  # Local backup
                image_cloudinary_url=cloudinary_url,
                image_cloudinary_id=cloudinary_id,
                latitude=latitude,
                longitude=longitude,
                action=action,
                timestamp=now()
            )

            return Response({
                'message': f'{action.capitalize()} recorded successfully!',
                'similarity': round(similarity, 4),
                'distance_from_office': int(distance)
            }, status=201)

        except Exception as e:
            print("❌ Attendance Error:", e)
            return Response({'error': str(e)}, status=500)
  
        
class OfficeLocationView(APIView):
    def post(self, request):
        serializer = OfficeLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def get(self, request):
        locations = OfficeLocation.objects.all()
        return Response(OfficeLocationSerializer(locations, many=True).data)

class OfficeLocationListView(ListAPIView):
    queryset = OfficeLocation.objects.all()
    serializer_class = OfficeLocationSerializer

class EmployeeListView(APIView):
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True, context={'request': request})
        return Response(serializer.data)
class AdminAttendanceLogsView(APIView):
    def get(self, request):
        date_filter = request.query_params.get('date', 'today')
        now = datetime.now()
        today_start = make_aware(datetime(now.year, now.month, now.day))

        if date_filter == 'yesterday':
            start = today_start - timedelta(days=1)
            end = today_start
        elif date_filter == 'last7days':
            start = today_start - timedelta(days=7)
            end = now
        else:  # today
            start = today_start
            end = now

        logs = Attendance.objects.filter(timestamp__range=(start, end)).select_related('employee', 'employee__office')
        data = []
        for log in logs:
            data.append({
                'id': log.id,
                'employee_name': log.employee.name,
                'employee_id': log.employee.employee_id,
                'image_url': log.image.url,
                'latitude': log.latitude,
                'longitude': log.longitude,
                'timestamp': log.timestamp,
                'action': log.action,
                'office_location_name': log.employee.office.name,
                'is_location_matched': True
            })

        return Response(data)

class EmployeeAttendanceLogsView(APIView):
    def get(self, request, employee_id):
        try:
            # Get employee
            employee = Employee.objects.get(employee_id=employee_id)
            
            # Get attendance logs for this employee
            logs = Attendance.objects.filter(employee=employee).order_by('-timestamp')
            
            data = []
            for log in logs:
                data.append({
                    'id': log.id,
                    'employee_name': log.employee.name,
                    'employee_id': log.employee.employee_id,
                    'image_url': log.image.url,
                    'latitude': log.latitude,
                    'longitude': log.longitude,
                    'timestamp': log.timestamp,
                    'action': log.action,
                    'office_location_name': log.employee.office.name,
                    'is_location_matched': True
                })

            return Response(data)
            
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=404)
        except Exception as e:
            print("❌ Employee Attendance Logs Error:", e)
            return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def location_alert(request):
    """Handle location alerts when employees move away from office"""
    try:
        employee_id = request.data.get('employee_id')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        distance = request.data.get('distance')
        timestamp = request.data.get('timestamp')

        if not all([employee_id, latitude, longitude, distance, timestamp]):
            return Response({'error': 'Missing required fields'}, status=400)

        # Get employee
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=404)

        # Create location alert
        LocationAlert.objects.create(
            employee=employee,
            latitude=latitude,
            longitude=longitude,
            distance=distance,
            timestamp=timestamp,
            office_name=employee.office.name
        )

        return Response({'message': 'Location alert created successfully'}, status=201)

    except Exception as e:
        print("❌ Location Alert Error:", e)
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def location_alerts(request):
    """Get all location alerts"""
    try:
        alerts = LocationAlert.objects.all().order_by('-timestamp')[:50]  # Last 50 alerts
        serializer = LocationAlertSerializer(alerts, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        print("❌ Location Alerts Error:", e)
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def employee_locations(request):
    """Get current locations of all employees"""
    try:
        # Get the latest location for each employee
        employees = Employee.objects.all()
        locations = []
        
        for employee in employees:
            # Get the latest location for this employee
            latest_location = EmployeeLocation.objects.filter(
                employee=employee
            ).order_by('-timestamp').first()
            
            # Check if employee should be marked as offline
            is_online = check_employee_online_status(employee)
            
            if latest_location and is_online:
                locations.append({
                    'employee_id': employee.employee_id,
                    'employee_name': employee.name,
                    'latitude': latest_location.latitude,
                    'longitude': latest_location.longitude,
                    'distance_from_office': latest_location.distance_from_office,
                    'is_in_office_radius': latest_location.is_in_office_radius,
                    'office_name': employee.office.name,
                    'office_latitude': employee.office.latitude,
                    'office_longitude': employee.office.longitude,
                    'office_radius': employee.office.radius_meters,
                    'timestamp': latest_location.timestamp.isoformat(),
                    'status': 'online'
                })
            else:
                # Employee is offline
                locations.append({
                    'employee_id': employee.employee_id,
                    'employee_name': employee.name,
                    'latitude': employee.office.latitude if employee.office else 0,
                    'longitude': employee.office.longitude if employee.office else 0,
                    'distance_from_office': 0,
                    'is_in_office_radius': False,
                    'office_name': employee.office.name if employee.office else 'Unknown',
                    'office_latitude': employee.office.latitude if employee.office else 0,
                    'office_longitude': employee.office.longitude if employee.office else 0,
                    'office_radius': employee.office.radius_meters if employee.office else 0,
                    'timestamp': latest_location.timestamp.isoformat() if latest_location else None,
                    'status': 'offline'
                })
        
        return Response(locations, status=200)
    except Exception as e:
        print("❌ Employee Locations Error:", e)
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def location_update(request):
    """Handle real-time location updates from employees"""
    try:
        print("📍 Location update received:", request.data)
        
        employee_id = request.data.get('employee_id')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        is_in_office_radius = request.data.get('is_in_office_radius', True)
        distance_from_office = request.data.get('distance_from_office', 0)
        is_sharing = request.data.get('is_sharing', True)  # New field to track sharing status
        
        print(f"📍 Processing location update for employee {employee_id}: lat={latitude}, lon={longitude}, in_radius={is_in_office_radius}, distance={distance_from_office}, sharing={is_sharing}")
        
        if not all([employee_id, latitude, longitude]):
            print("❌ Missing required fields")
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            print(f"✅ Employee found: {employee.name}")
        except Employee.DoesNotExist:
            print(f"❌ Employee not found: {employee_id}")
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if is_sharing:
            # Create or update employee location
            location, created = EmployeeLocation.objects.update_or_create(
                employee=employee,
                is_active=True,
                defaults={
                    'latitude': latitude,
                    'longitude': longitude,
                    'is_in_office_radius': is_in_office_radius,
                    'distance_from_office': distance_from_office,
                    'timestamp': timezone.now()
                }
            )
            
            print(f"✅ Location {'created' if created else 'updated'}: {location}")
            
            # If employee is outside radius, create location alert
            if not is_in_office_radius:
                alert = LocationAlert.objects.create(
                    employee=employee,
                    latitude=latitude,
                    longitude=longitude,
                    distance=distance_from_office / 1000,  # Convert to km
                    office_name=employee.office.name
                )
                print(f"⚠️ Location alert created: {alert}")
        else:
            # Mark employee as offline (not sharing location)
            EmployeeLocation.objects.filter(employee=employee, is_active=True).update(is_active=False)
            print(f"🔄 Employee {employee.name} marked as offline")
        
        response_data = {
            'message': 'Location updated successfully',
            'is_in_office_radius': is_in_office_radius,
            'distance': distance_from_office,
            'is_sharing': is_sharing
        }
        print(f"✅ Location update response: {response_data}")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Location update error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_employee_status(request):
    """Manually trigger employee status update"""
    try:
        print("🔄 Manual employee status update requested")
        
        employees = Employee.objects.all()
        updated_count = 0
        
        for employee in employees:
            # Check if employee should be marked as offline
            is_online = check_employee_online_status(employee)
            
            # Get the latest location record
            latest_location = EmployeeLocation.objects.filter(
                employee=employee
            ).order_by('-timestamp').first()
            
            if latest_location:
                # Update the is_active status based on online check
                if latest_location.is_active != is_online:
                    latest_location.is_active = is_online
                    latest_location.save()
                    updated_count += 1
                    print(f"✅ Updated {employee.name} to {'online' if is_online else 'offline'}")
        
        return Response({
            'message': f'Employee status update completed. Updated {updated_count} employees.',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Employee status update error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def check_employee_online_status(employee):
    """
    Check if employee should be marked as offline based on:
    1. No location update for more than 10 minutes (if they were sharing)
    2. No login for more than 24 hours (more reasonable for daily work)
    """
    now = timezone.now()
    
    # Get the latest attendance (login/logout)
    latest_attendance = Attendance.objects.filter(
        employee=employee
    ).order_by('-timestamp').first()
    
    # Get the latest location update
    latest_location = EmployeeLocation.objects.filter(
        employee=employee
    ).order_by('-timestamp').first()
    
    # If employee has a recent location update (within 10 minutes), they're online
    if latest_location and latest_location.is_active:
        time_since_location = now - latest_location.timestamp
        if time_since_location <= timedelta(minutes=10):
            print(f"✅ Employee {employee.name} has recent location update ({time_since_location.total_seconds()/60:.1f} minutes ago) - marking online")
            return True
    
    # Check if employee hasn't logged in for more than 24 hours (more reasonable)
    if latest_attendance:
        time_since_login = now - latest_attendance.timestamp
        if time_since_login > timedelta(hours=24):
            print(f"🕐 Employee {employee.name} hasn't logged in for {time_since_login.total_seconds()/3600:.1f} hours - marking offline")
            return False
    
    # If employee has location data but it's older than 10 minutes, they're offline
    if latest_location and latest_location.is_active:
        time_since_location = now - latest_location.timestamp
        if time_since_location > timedelta(minutes=10):
            print(f"📍 Employee {employee.name} hasn't sent location for {time_since_location.total_seconds()/60:.1f} minutes - marking offline")
            return False
    
    # Default to offline if no recent activity
    return False

@api_view(['GET'])
def live_employee_locations(request):
    """Get live locations of all employees (including offline ones)"""
    try:
        print("📡 Live employee locations request received")
        
        # Get all employees
        employees = Employee.objects.all().select_related('office')
        
        data = []
        for employee in employees:
            # Get the most recent location for this employee
            latest_location = EmployeeLocation.objects.filter(
                employee=employee
            ).order_by('-timestamp').first()
            
            # Check if employee should be marked as offline
            is_online = check_employee_online_status(employee)
            
            if latest_location and latest_location.is_active and is_online:
                # Employee is online and sharing location
                data.append({
                    'employee_id': employee.employee_id,
                    'employee_name': employee.name,
                    'latitude': latest_location.latitude,
                    'longitude': latest_location.longitude,
                    'is_in_office_radius': latest_location.is_in_office_radius,
                    'distance_from_office': latest_location.distance_from_office,
                    'office_name': employee.office.name,
                    'office_latitude': employee.office.latitude,
                    'office_longitude': employee.office.longitude,
                    'office_radius': employee.office.radius_meters,
                    'last_updated': latest_location.timestamp.isoformat(),
                    'status': 'online',
                    'is_sharing': True
                })
            elif latest_location and latest_location.is_active:
                # Employee has location data but is offline (location too old)
                data.append({
                    'employee_id': employee.employee_id,
                    'employee_name': employee.name,
                    'latitude': latest_location.latitude,
                    'longitude': latest_location.longitude,
                    'is_in_office_radius': latest_location.is_in_office_radius,
                    'distance_from_office': latest_location.distance_from_office,
                    'office_name': employee.office.name,
                    'office_latitude': employee.office.latitude,
                    'office_longitude': employee.office.longitude,
                    'office_radius': employee.office.radius_meters,
                    'last_updated': latest_location.timestamp.isoformat(),
                    'status': 'offline',
                    'is_sharing': False
                })
            else:
                # Employee is offline with no recent location
                data.append({
                    'employee_id': employee.employee_id,
                    'employee_name': employee.name,
                    'latitude': employee.office.latitude if employee.office else 0,
                    'longitude': employee.office.longitude if employee.office else 0,
                    'is_in_office_radius': False,
                    'distance_from_office': 0,
                    'office_name': employee.office.name if employee.office else 'Unknown',
                    'office_latitude': employee.office.latitude if employee.office else 0,
                    'office_longitude': employee.office.longitude if employee.office else 0,
                    'office_radius': employee.office.radius_meters if employee.office else 0,
                    'last_updated': latest_location.timestamp.isoformat() if latest_location else None,
                    'status': 'offline',
                    'is_sharing': False
                })
        
        print(f"✅ Returning {len(data)} employee locations (online + offline)")
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Live employee locations error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
