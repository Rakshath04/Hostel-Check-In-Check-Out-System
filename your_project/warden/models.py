from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    dob = models.DateField()
    face_encoding = models.BinaryField(default=b'')  # To store the face encoding

    def __str__(self):
        return self.name

class CheckInCheckOut(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Check-in: {self.check_in_time}, Check-out: {self.check_out_time or 'Not yet checked out'}"

