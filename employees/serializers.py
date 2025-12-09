from rest_framework import serializers
from .models import Employee, Attendance, OfficeLocation, LocationAlert



class AttendanceSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    cloudinary_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = '__all__'  # or include 'image_url' explicitly if not using all fields

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            else:
                return obj.image.url
        return None

    def get_cloudinary_image_url(self, obj):
        # Return Cloudinary URL if available, otherwise fallback to local
        if obj.image_cloudinary_url:
            return obj.image_cloudinary_url
        return self.get_image_url(obj)

# employees/serializers.py

class OfficeLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeLocation
        fields =  ['id', 'name', 'latitude', 'longitude', 'radius_meters']  # include 'id' and 'name'

class EmployeeSerializer(serializers.ModelSerializer):
    office_latitude = serializers.FloatField(source='office.latitude')
    office_longitude = serializers.FloatField(source='office.longitude')
    office_radius = serializers.FloatField(source='office.radius_meters')
    office_name = serializers.CharField(source='office.name')
    face_image_url = serializers.SerializerMethodField()
    cloudinary_face_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'name', 'employee_id', 'face_image', 'face_image_url', 'cloudinary_face_image_url', 'office_latitude', 'office_longitude', 'office_radius', 'office_name']

    def get_face_image_url(self, obj):
        request = self.context.get('request')
        if obj.face_image:
            if request:
                return request.build_absolute_uri(obj.face_image.url)
            else:
                return obj.face_image.url
        return None

    def get_cloudinary_face_image_url(self, obj):
        # Return Cloudinary URL if available, otherwise fallback to local
        if obj.face_image_cloudinary_url:
            return obj.face_image_cloudinary_url
        return self.get_face_image_url(obj)

class LocationAlertSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name')
    employee_id = serializers.CharField(source='employee.employee_id')
    
    class Meta:
        model = LocationAlert
        fields = ['id', 'employee_id', 'employee_name', 'latitude', 'longitude', 'distance', 'timestamp', 'office_name']
