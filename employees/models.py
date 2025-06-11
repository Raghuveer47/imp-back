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
    office = models.ForeignKey('OfficeLocation', on_delete=models.CASCADE)
    
    # 🧠 New field to store face encodings as binary
    face_encoding = models.BinaryField(null=True, blank=True)

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='attendance_photos/')
    latitude = models.FloatField()
    longitude = models.FloatField()
    action = models.CharField(max_length=10, default='login')



