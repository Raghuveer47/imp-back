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
from .models import Employee, Attendance, OfficeLocation
from .serializers import EmployeeSerializer, AttendanceSerializer, OfficeLocationSerializer
from .utils import get_face_encoding_from_base64, is_within_location
from .utils import is_within_location  # 🔁 utility to compute distance

import face_recognition
import numpy as np
import base64
import io
from deepface import DeepFace
import cv2
from PIL import Image

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
        img_array = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Get descriptor from DeepFace
        representation = DeepFace.represent(img_path=img, model_name='Facenet')[0]
        descriptor = representation["embedding"]

        return Response({"descriptor": descriptor}, status=status.HTTP_200_OK)

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

            # Decode and save face image
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

            # Save employee
            Employee.objects.create(
                name=name,
                employee_id=employee_id,
                face_image=image_file,
                office=office_instance,
                face_encoding=descriptor_array.tobytes()  # now 128-D float32
            )

            return Response({'message': 'Employee registered successfully!'}, status=201)

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

            if similarity < 0.85:
                return Response({'error': 'Face does not match'}, status=403)

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

            # ✅ Save image
            if "," in face_image_base64:
                face_image_base64 = face_image_base64.split(",")[1]
            image_data = base64.b64decode(face_image_base64)
            image_file = ContentFile(image_data, name=f"{employee_id}_{action}.jpg")

            # ✅ Save attendance
            Attendance.objects.create(
                employee=employee,
                image=image_file,
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
        serializer = EmployeeSerializer(employees, many=True)
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
