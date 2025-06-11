from rest_framework import serializers
from .models import Employee, Attendance, OfficeLocation



class AttendanceSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = '__all__'  # or include 'image_url' explicitly if not using all fields

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

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

    class Meta:
        model = Employee
        fields = ['id', 'name', 'employee_id', 'face_image', 'office_latitude', 'office_longitude', 'office_radius', 'office_name']
