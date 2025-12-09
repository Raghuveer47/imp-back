from django.db import models




class OfficeLocation(models.Model):
    name = models.CharField(max_length=100, default="Main Office")
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius_meters = models.FloatField(default=100.0)  # Allowed radius

    def __str__(self):
        return self.name  # Allowed radius
    
class Employee(models.Model):
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=100, unique=True)
    face_image = models.ImageField(upload_to='face_images/')
    # 🖼️ Cloudinary URL for face image
    face_image_cloudinary_url = models.URLField(max_length=500, blank=True, null=True)
    face_image_cloudinary_id = models.CharField(max_length=200, blank=True, null=True)
    office = models.ForeignKey('OfficeLocation', on_delete=models.CASCADE)
    
    # 🧠 New field to store face encodings as binary
    face_encoding = models.BinaryField(null=True, blank=True)

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='attendance_photos/')
    # 🖼️ Cloudinary URL for attendance image
    image_cloudinary_url = models.URLField(max_length=500, blank=True, null=True)
    image_cloudinary_id = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    action = models.CharField(max_length=10, default='login')

class LocationAlert(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    distance = models.FloatField()  # Distance from office in km
    timestamp = models.DateTimeField(auto_now_add=True)
    office_name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.employee.name} - {self.distance:.2f}km away at {self.timestamp}"

class EmployeeLocation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_in_office_radius = models.BooleanField(default=True)
    distance_from_office = models.FloatField()  # Distance in meters
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # To track if location sharing is active
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.employee.name} - {self.distance_from_office:.0f}m from office at {self.timestamp}"



